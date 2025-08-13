import json
import os
import signal
import socket
import subprocess
import sys
import time

import pytest
from openai import OpenAI

# Model to use for all tests
TEST_MODEL = "gpt-4o-mini"


def check_openai_key():
    """Check if OpenAI key is configured in llm"""
    try:
        result = subprocess.run(
            ["llm", "keys"],
            capture_output=True,
            text=True,
            check=True
        )
        if "openai" not in result.stdout:
            raise RuntimeError(
                "OpenAI key not found in 'llm keys' output.\n"
                "Please set your OpenAI API key by running:\n"
                "  llm keys set openai\n"
                "Then enter your OpenAI API key when prompted."
            )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to run 'llm keys': {e}\n"
            "Make sure the 'llm' command is installed and available in your PATH."
        )
    except FileNotFoundError:
        raise RuntimeError(
            "'llm' command not found.\n"
            "Please install it first following the guide in README.md"
        )


# Run the check when the module is imported
check_openai_key()


def get_free_port():
    """Get a free port number"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


@pytest.fixture(scope="session")
def llm_api_server():
    """Start and stop the LLM server for tests"""
    # Get a random free port
    port = get_free_port()

    # Start the server
    process = subprocess.Popen(
        [sys.executable, "-m", "llm", "api", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid,
    )

    # Wait for server to start with retries
    max_retries = 10
    for i in range(max_retries):
        time.sleep(0.5)
        # Check if server started successfully
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            raise RuntimeError(f"Server failed to start: {stderr.decode()}")

        # Try to connect to the server
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect(("localhost", port))
                break
        except (socket.timeout, ConnectionRefusedError) as e:
            if i == max_retries - 1:
                # Clean up process before raising
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                raise RuntimeError(
                    "Server failed to start on port "
                    f"{port} after {max_retries} attempts"
                ) from e

    yield f"http://localhost:{port}"

    # Clean up: Stop the server
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        # Force kill if graceful shutdown fails
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        process.wait()


@pytest.fixture(scope="session")
def client(llm_api_server):
    """Create OpenAI client configured for local server"""
    return OpenAI(
        base_url=f"{llm_api_server}/v1",
        api_key="dummy-key",  # LLM server doesn't require auth
    )


def test_list_models(client):
    """Test listing available models"""
    models = client.models.list()
    assert hasattr(models, "data")
    assert len(models.data) > 0
    # Check model structure
    for model in models.data:
        assert hasattr(model, "id")
        assert hasattr(model, "object")
        assert model.object == "model"


def test_chat_completion_non_streaming(client):
    """Test non-streaming chat completion"""
    response = client.chat.completions.create(
        model=TEST_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, World!' and nothing else."},
        ],
        stream=False,
        temperature=0.7,
        max_tokens=50,
    )

    # Check response structure
    assert response.id.startswith("chatcmpl-")
    assert response.object == "chat.completion"
    assert len(response.choices) == 1

    choice = response.choices[0]
    assert choice.index == 0
    assert choice.message.role == "assistant"
    assert isinstance(choice.message.content, str)
    assert len(choice.message.content) > 0
    assert choice.finish_reason == "stop"

    # Check usage
    assert hasattr(response, "usage")
    assert response.usage.prompt_tokens > 0
    assert response.usage.completion_tokens > 0
    assert response.usage.total_tokens == (
        response.usage.prompt_tokens + response.usage.completion_tokens
    )


def test_chat_completion_streaming(client):
    """Test streaming chat completion"""
    stream = client.chat.completions.create(
        model=TEST_MODEL,
        messages=[{"role": "user", "content": "Count from 1 to 3."}],
        stream=True,
        temperature=0.5,
        max_tokens=30,
    )

    chunks = []
    completion_id = None

    for chunk in stream:
        chunks.append(chunk)

        # Check chunk structure
        assert chunk.object == "chat.completion.chunk"
        assert len(chunk.choices) == 1

        # All chunks should have the same ID
        if completion_id is None:
            completion_id = chunk.id
            assert completion_id.startswith("chatcmpl-")
        else:
            assert chunk.id == completion_id

        choice = chunk.choices[0]
        assert choice.index == 0

        # Either delta content or finish_reason should be present
        if choice.finish_reason is None:
            assert hasattr(choice.delta, "content")
        else:
            assert choice.finish_reason == "stop"

    # Should have received multiple chunks
    assert len(chunks) > 1

    # Last chunk should have finish_reason
    assert chunks[-1].choices[0].finish_reason == "stop"

    # Reconstruct the full response
    full_content = "".join(
        chunk.choices[0].delta.content
        for chunk in chunks
        if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content
    )
    assert len(full_content) > 0


def test_multi_turn_conversation(client):
    """Test multi-turn conversation"""
    messages = [
        {"role": "system", "content": "You are a math tutor."},
        {"role": "user", "content": "What is 2 + 2?"},
        {"role": "assistant", "content": "2 + 2 equals 4."},
        {"role": "user", "content": "And what is that times 3?"},
    ]

    response = client.chat.completions.create(
        model=TEST_MODEL, messages=messages, stream=False, temperature=0.3
    )

    # Check that the response acknowledges the previous context
    content = response.choices[0].message.content.lower()
    # The response should reference the number 12 (4 * 3)
    assert "12" in content or "twelve" in content


def test_system_prompt_only(client):
    """Test with only system prompt"""
    response = client.chat.completions.create(
        model=TEST_MODEL,
        messages=[
            {"role": "system", "content": "Generate a haiku about Python programming."}
        ],
        stream=False,
    )

    # Should get a response even with only system prompt
    assert len(response.choices[0].message.content) > 0


def test_error_handling_invalid_model(client):
    """Test error handling for invalid model"""
    with pytest.raises(Exception) as exc_info:
        client.chat.completions.create(
            model="invalid-model-name",
            messages=[{"role": "user", "content": "Hello"}],
            stream=False,
        )

    # Should get a meaningful error
    assert "not found" in str(exc_info.value).lower()


def test_streaming_with_multiple_messages(client):
    """Test streaming with system and user messages"""
    stream = client.chat.completions.create(
        model=TEST_MODEL,
        messages=[
            {"role": "system", "content": "You are a poet."},
            {"role": "user", "content": "Write one line of poetry."},
        ],
        stream=True,
        max_tokens=20,
    )

    chunks = list(stream)
    assert len(chunks) > 0

    # Verify streaming response format
    for chunk in chunks[:-1]:  # All but last chunk
        if hasattr(chunk.choices[0].delta, "content"):
            assert chunk.choices[0].delta.content is not None


def test_with_tools(client):
    """Test completion with tools."""
    response = client.chat.completions.create(
        model=TEST_MODEL,
        messages=[{"role": "user", "content": "What's the weather in San Francisco?"}],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather in a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": (
                                    "The city and state, e.g. San Francisco, CA"
                                ),
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"],
                            },
                        },
                        "required": ["location"],
                    },
                },
            }
        ],
    )

    # Validate response
    assert response.id.startswith("chatcmpl-")
    assert response.object == "chat.completion"
    assert len(response.choices) == 1

    # Check if model made a tool call or regular response
    choice = response.choices[0]
    if hasattr(choice.message, "tool_calls") and choice.message.tool_calls:
        # Model made a tool call
        assert len(choice.message.tool_calls) > 0
        tool_call = choice.message.tool_calls[0]
        assert tool_call.type == "function"
        assert tool_call.function.name == "get_weather"
        assert "San Francisco" in tool_call.function.arguments
    else:
        # Model responded without tool call
        assert choice.message.content is not None
        assert len(choice.message.content) > 0


def test_with_tool_results(client):
    """Test completion with tool results."""
    # First, make a request that should trigger a tool call
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather in a location",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string"}},
                    "required": ["location"],
                },
            },
        }
    ]

    # Step 1: Get the assistant to make a tool call
    first_response = client.chat.completions.create(
        model=TEST_MODEL,
        messages=[{"role": "user", "content": "What's the weather in San Francisco?"}],
        tools=tools,
    )

    # Check if the model made a tool call
    if not (
        hasattr(first_response.choices[0].message, "tool_calls")
        and first_response.choices[0].message.tool_calls
    ):
        # If no tool call was made, skip this test
        pytest.fail("Model did not make a tool call")

    # Step 2: Extract the tool call details
    tool_call = first_response.choices[0].message.tool_calls[0]

    # Step 3: Make a second request with the tool result
    assistant_message = {
        "role": "assistant",
        "tool_calls": [
            tc.model_dump() for tc in first_response.choices[0].message.tool_calls
        ],
    }
    # Only include content if it's not None
    if first_response.choices[0].message.content is not None:
        assistant_message["content"] = first_response.choices[0].message.content

    messages = [
        {"role": "user", "content": "What's the weather in San Francisco?"},
        assistant_message,
        {
            "role": "tool",
            "content": "72°F, sunny",
            "tool_call_id": tool_call.id,
        },
    ]

    response = client.chat.completions.create(
        model=TEST_MODEL,
        messages=messages,
        tools=tools,
    )

    # Validate response
    assert response.id.startswith("chatcmpl-")
    assert response.object == "chat.completion"
    assert len(response.choices) == 1
    assert response.choices[0].message.role == "assistant"
    assert response.choices[0].message.content is not None
    # Should mention the weather result
    content_lower = response.choices[0].message.content.lower()
    assert "72" in response.choices[0].message.content or "sunny" in content_lower


def test_with_schema(client):
    """Test completion with response_format schema."""
    response = client.chat.completions.create(
        model=TEST_MODEL,
        messages=[{"role": "user", "content": "Generate a person with name and age"}],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "person",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"},
                    },
                    "required": ["name", "age"],
                },
            },
        },
    )

    # Validate response
    assert response.id.startswith("chatcmpl-")
    assert response.object == "chat.completion"
    assert len(response.choices) == 1

    # Parse and validate JSON content
    content = response.choices[0].message.content
    assert content is not None

    # Should be valid JSON matching the schema
    try:
        parsed = json.loads(content)
        assert "name" in parsed
        assert "age" in parsed
        assert isinstance(parsed["name"], str)
        assert isinstance(parsed["age"], int)
    except json.JSONDecodeError:
        pytest.fail("Response content is not valid JSON")


def test_multiple_messages_conversation(client):
    """Test conversation with multiple messages asking about first message."""
    first_message = "My favorite color is blue"

    messages = [
        {"role": "user", "content": first_message},
        {"role": "assistant", "content": "That's nice! Blue is a lovely color."},
        {"role": "user", "content": "What was the first thing I told you?"},
    ]

    response = client.chat.completions.create(
        model=TEST_MODEL,
        messages=messages,
    )

    # Validate response structure
    assert response.id.startswith("chatcmpl-")
    assert response.object == "chat.completion"
    assert len(response.choices) == 1
    assert response.choices[0].message.role == "assistant"
    assert response.choices[0].message.content is not None

    # Validate that the assistant mentions the first message content
    response_content = response.choices[0].message.content.lower()
    assert "blue" in response_content or "color" in response_content


def test_model_capabilities(client):
    """Test model capabilities check."""
    # Test with a model that doesn't support tools
    # This should either work or return an appropriate error
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "test",
                        "description": "Test function",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                        },
                    },
                }
            ],
        )
        # If it succeeds, model supports tools
        assert response.id.startswith("chatcmpl-")
    except Exception as e:
        # If it fails, should be because model doesn't support tools
        assert "tools" in str(e).lower() or "not supported" in str(e).lower()

    # Test with a model that doesn't support schema
    try:
        response = client.chat.completions.create(
            model=TEST_MODEL,
            messages=[{"role": "user", "content": "Hello"}],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "test",
                    "schema": {"type": "object", "properties": {}},
                },
            },
        )
        # If it succeeds, model supports schema
        assert response.id.startswith("chatcmpl-")
    except Exception as e:
        # If it fails, should be because model doesn't support schema
        assert "schema" in str(e).lower() or "not supported" in str(e).lower()

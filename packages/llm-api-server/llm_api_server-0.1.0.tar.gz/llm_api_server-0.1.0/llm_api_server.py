import json
import logging
import time
import uuid
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

import click
import llm
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from llm import Prompt, Response, ToolCall, ToolResult, hookimpl
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Any] = None
    response_format: Optional[Dict[str, Any]] = None


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str
    logprobs: Optional[Dict[str, Any]] = None


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Dict[str, int]


class ChatCompletionStreamChoice(BaseModel):
    index: int
    delta: Dict[str, Any]
    finish_reason: Optional[str] = None


class ChatCompletionStreamResponse(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChatCompletionStreamChoice]


def convert_openai_tools_to_llm(
    openai_tools: Optional[List[Dict[str, Any]]],
) -> List[llm.Tool]:
    """Convert OpenAI-format tools to llm.Tool objects."""
    if not openai_tools:
        return []

    llm_tools = []
    for tool in openai_tools:
        if tool.get("type") == "function":
            function = tool.get("function", {})
            tool_name = function.get("name", "")
            llm_tool = llm.Tool(
                name=tool_name,
                description=function.get("description", ""),
                input_schema=function.get("parameters", {}),
                implementation=lambda name=tool_name, **kwargs: (
                    f"Tool {name} called with {kwargs}"
                ),
            )
            llm_tools.append(llm_tool)
    return llm_tools


def convert_llm_tool_calls_to_openai(
    tool_calls: List[ToolCall],
) -> List[Dict[str, Any]]:
    """Convert llm.ToolCall objects to OpenAI format."""
    return [
        {
            "id": tc.tool_call_id or f"call_{uuid.uuid4().hex[:8]}",
            "type": "function",
            "function": {
                "name": tc.name,
                "arguments": json.dumps(tc.arguments),
            },
        }
        for tc in tool_calls
    ]


def extract_response_format_schema(
    response_format: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """Extract JSON schema from OpenAI response_format."""
    if not response_format or response_format.get("type") != "json_schema":
        return None

    return response_format.get("json_schema", {}).get("schema", {})


# Message processing utilities
def extract_system_prompt(messages: List[ChatMessage]) -> Optional[str]:
    """Extract and combine all system messages from the conversation."""
    system_messages = [
        msg.content for msg in messages if msg.role == "system" and msg.content
    ]
    return "\n\n".join(system_messages) if system_messages else None


def create_tool_result(
    tool_msg: ChatMessage, assistant_tool_calls: List[Dict[str, Any]]
) -> ToolResult:
    """Create a ToolResult from a tool message and assistant's tool calls."""
    tool_name = ""
    for tc in assistant_tool_calls:
        if tc.get("id") == tool_msg.tool_call_id:
            tool_name = tc.get("function", {}).get("name", "")
            break

    return ToolResult(
        name=tool_name,
        output=tool_msg.content or "",
        tool_call_id=tool_msg.tool_call_id,
    )


def process_conversation_history(
    messages: List[ChatMessage],
    model: Any,
    conversation: Any,
    llm_tools: List[llm.Tool],
    system_prompt: Optional[str],
) -> Tuple[Optional[str], List[ToolResult]]:
    """Process conversation history and return current prompt and tool results."""
    i = 0
    current_prompt = None
    current_tool_results = []

    while i < len(messages):
        msg = messages[i]
        if msg.role == "user":
            # Check if there's an assistant response after this
            if i + 1 < len(messages) and messages[i + 1].role == "assistant":
                assistant_msg = messages[i + 1]

                # Create and add response to conversation
                response = _create_response_from_messages(
                    user_msg=msg,
                    assistant_msg=assistant_msg,
                    model=model,
                    conversation=conversation,
                    llm_tools=llm_tools,
                    system_prompt=system_prompt if i == 0 else None,
                )
                conversation.responses.append(response)

                # Skip to after assistant message
                i += 2

                # Process any tool messages that follow
                tool_results_for_response = _collect_tool_results(
                    messages, i, assistant_msg.tool_calls or []
                )

                # Update index based on tool results processed
                i += len(tool_results_for_response)

                # Handle continuation after tool results
                if tool_results_for_response and i < len(messages):
                    i = _handle_tool_continuation(
                        messages,
                        i,
                        model,
                        conversation,
                        llm_tools,
                        tool_results_for_response,
                    )
                # Continue processing messages
                continue
            else:
                # This is the current user message to respond to
                current_prompt = msg.content
                break
        else:
            # Skip non-user messages
            i += 1

    # Handle edge cases
    if current_prompt is None:
        logger.info("No current prompt found, handling final message")
        current_prompt, current_tool_results = _handle_final_message(
            messages, system_prompt
        )

    logger.info(f"Returning prompt: {current_prompt[:50] if current_prompt else None}")
    return current_prompt, current_tool_results


def _create_response_from_messages(
    user_msg: ChatMessage,
    assistant_msg: ChatMessage,
    model: Any,
    conversation: Any,
    llm_tools: List[llm.Tool],
    system_prompt: Optional[str],
) -> Response:
    """Create a Response object from user and assistant messages."""
    response = Response(
        prompt=Prompt(
            prompt=user_msg.content,
            model=model,
            system=system_prompt,
            tools=llm_tools,
            tool_results=[],
            options=model.Options(),
        ),
        model=model,
        stream=False,
        conversation=conversation,
    )

    # Set response as completed
    response._done = True
    response._chunks = [assistant_msg.content or ""]
    response._tool_calls = []
    response.attachments = []

    # Add tool calls if present
    if assistant_msg.tool_calls:
        for tc in assistant_msg.tool_calls:
            tool_call = ToolCall(
                name=tc.get("function", {}).get("name", ""),
                arguments=json.loads(tc.get("function", {}).get("arguments", "{}")),
                tool_call_id=tc.get("id"),
            )
            response._tool_calls.append(tool_call)

    return response


def _collect_tool_results(
    messages: List[ChatMessage],
    start_index: int,
    assistant_tool_calls: List[Dict[str, Any]],
) -> List[ToolResult]:
    """Collect tool results starting from the given index."""
    tool_results = []
    i = start_index

    while i < len(messages) and messages[i].role == "tool":
        tool_result = create_tool_result(messages[i], assistant_tool_calls)
        tool_results.append(tool_result)
        i += 1

    return tool_results


def _handle_tool_continuation(
    messages: List[ChatMessage],
    index: int,
    model: Any,
    conversation: Any,
    llm_tools: List[llm.Tool],
    tool_results: List[ToolResult],
) -> int:
    """Handle continuation after tool execution."""
    if (
        index < len(messages)
        and messages[index].role == "user"
        and index + 1 < len(messages)
        and messages[index + 1].role == "assistant"
    ):
        # Create response for tool results continuation
        tool_response = Response(
            prompt=Prompt(
                prompt=messages[index].content or "",
                model=model,
                system=None,
                tools=llm_tools,
                tool_results=tool_results,
                options=model.Options(),
            ),
            model=model,
            stream=False,
            conversation=conversation,
        )
        tool_response._done = True
        tool_response._chunks = [messages[index + 1].content or ""]
        tool_response._tool_calls = []
        tool_response.attachments = []
        conversation.responses.append(tool_response)
        return index + 2

    return index


def _handle_final_message(
    messages: List[ChatMessage],
    system_prompt: Optional[str],
) -> Tuple[str, List[ToolResult]]:
    """Handle edge cases for the final message."""
    current_tool_results = []

    if messages and messages[-1].role == "tool":
        # Continue after tool results
        current_prompt = ""

        # Find the last assistant message with tool calls
        for i in range(len(messages) - 1, -1, -1):
            if messages[i].role == "assistant":
                assistant_msg = messages[i]
                if assistant_msg.tool_calls:
                    # Collect tool results
                    for j in range(i + 1, len(messages)):
                        if messages[j].role == "tool":
                            tool_result = create_tool_result(
                                messages[j], assistant_msg.tool_calls
                            )
                            current_tool_results.append(tool_result)
                break
    elif system_prompt:
        current_prompt = ""
    else:
        raise HTTPException(status_code=400, detail="No message to respond to")

    return current_prompt, current_tool_results


def _load_and_validate_model(request: ChatCompletionRequest) -> Any:
    """Load the model and validate its capabilities."""
    try:
        model = llm.get_model(request.model)
        logger.info(f"Successfully loaded model: {request.model}")
    except Exception as e:
        logger.error(f"Model not found: {request.model} - Error: {str(e)}")
        raise HTTPException(
            status_code=404, detail=f"Model '{request.model}' not found: {str(e)}"
        ) from e

    # Check if model supports tools/schema
    supports_tools = hasattr(model, "supports_tools") and model.supports_tools
    supports_schema = hasattr(model, "supports_schema") and model.supports_schema

    if request.tools and not supports_tools:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{request.model}' does not support tools",
        )

    if request.response_format and not supports_schema:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{request.model}' does not support response_format/schema",
        )

    return model


def _prepare_model_options(request: ChatCompletionRequest) -> Dict[str, Any]:
    """Prepare model options from request."""
    options = {}
    if request.temperature is not None:
        options["temperature"] = request.temperature
    if request.max_tokens is not None:
        options["max_tokens"] = request.max_tokens
    return options


def _generate_non_streaming_response(
    conversation: Any,
    current_prompt: Optional[str],
    system_prompt: Optional[str],
    options: Dict[str, Any],
    request: ChatCompletionRequest,
    llm_tools: List[llm.Tool],
    current_tool_results: List[ToolResult],
    schema: Optional[Dict[str, Any]],
    model: Any,
) -> ChatCompletionResponse:
    """Generate a non-streaming chat completion response."""
    try:
        response = conversation.prompt(
            current_prompt or "",
            system=system_prompt,
            tools=llm_tools,
            tool_results=current_tool_results if current_tool_results else None,
            schema=schema,
            **options,
        )
        response_text = response.text()

        # Get tool calls if any
        supports_tools = hasattr(model, "supports_tools") and model.supports_tools
        tool_calls = response.tool_calls() if supports_tools else []
    except Exception as e:
        _handle_generation_error(e)

    # Create response
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
    created = int(time.time())

    # Get usage information
    usage_info = _get_usage_info(response, request.messages, response_text)

    return ChatCompletionResponse(
        id=completion_id,
        created=created,
        model=request.model,
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatMessage(
                    role="assistant",
                    content=response_text if not tool_calls else None,
                    tool_calls=convert_llm_tool_calls_to_openai(tool_calls)
                    if tool_calls
                    else None,
                ),
                finish_reason="tool_calls" if tool_calls else "stop",
            )
        ],
        usage=usage_info,
    )


def _handle_generation_error(e: Exception) -> None:
    """Handle errors during response generation."""
    error_message = str(e)
    if "APIConnectionError" in error_message or "Connection error" in error_message:
        raise HTTPException(
            status_code=503,
            detail=(
                "Model API connection error. Make sure the model is "
                "properly configured with API keys."
            ),
        ) from e
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {error_message}",
        ) from e


def _get_usage_info(
    response: Any, messages: List[ChatMessage], response_text: str
) -> Dict[str, int]:
    """Get token usage information from response or estimate it."""
    if usage_data := response.usage():
        return {
            "prompt_tokens": usage_data.input,
            "completion_tokens": usage_data.output,
            "total_tokens": (usage_data.input or 0) + (usage_data.output or 0),
        }
    else:
        # Fallback to approximation
        prompt_tokens = (
            sum(len(msg.content.split()) for msg in messages if msg.content) * 4 // 3
        )
        completion_tokens = len(response_text.split()) * 4 // 3
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }


@hookimpl
def register_commands(cli):
    @cli.command(name="api")
    @click.option("--host", default="127.0.0.1", help="Host to bind to")
    @click.option("--port", default=8000, type=int, help="Port to bind to")
    @click.option("--reload", is_flag=True, help="Enable auto-reload")
    @click.option(
        "--log-level",
        default="ERROR",
        type=click.Choice(
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
        ),
        help="Set the logging level (default: ERROR)",
    )
    def server(host: str, port: int, reload: bool, log_level: str):
        """Start a FastAPI server with OpenAI-compatible API endpoints"""
        # Configure logging based on the log level flag
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        # Set uvicorn logger levels
        logging.getLogger("uvicorn").setLevel(log_level.upper())
        logging.getLogger("uvicorn.error").setLevel(log_level.upper())
        logging.getLogger("uvicorn.access").setLevel(log_level.upper())

        click.echo(f"Starting LLM server on {host}:{port}")

        if reload:
            uvicorn.run(
                "llm_api_server:create_app",
                host=host,
                port=port,
                reload=True,
                factory=True,
            )
        else:
            app = create_app()
            uvicorn.run(app, host=host, port=port, reload=False)


def create_app() -> FastAPI:
    app = FastAPI(title="LLM Server", version="0.1.0")

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all incoming requests"""
        try:
            response = await call_next(request)
            logger.info(
                f"Response: {response.status_code} for {request.method} "
                f"{request.url.path}"
            )
            return response
        except Exception as e:
            logger.error(
                f"Error processing {request.method} {request.url.path}: {str(e)}"
            )
            raise

    @app.get("/v1/models")
    async def list_models():
        """List all available models"""
        models = []
        for model in llm.get_models():
            models.append(
                {
                    "id": model.model_id,
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "system",
                }
            )

        return {"object": "list", "data": models}

    @app.post("/v1/chat/completions")
    async def chat_completions(request: ChatCompletionRequest):
        """OpenAI-compatible chat completions endpoint"""
        logger.info(f"Chat completion request - Model: {request.model}")
        logger.info(f"Messages: {len(request.messages)} messages")
        logger.info(f"Stream: {request.stream}")

        # Load and validate model
        model = _load_and_validate_model(request)

        # Convert tools and extract schema
        llm_tools = convert_openai_tools_to_llm(request.tools)
        schema = extract_response_format_schema(request.response_format)

        # Create conversation
        conversation = model.conversation(tools=llm_tools)

        # Extract system prompt and process conversation history
        system_prompt = extract_system_prompt(request.messages)
        logger.info(f"System prompt: {system_prompt}")
        logger.info(f"Processing {len(request.messages)} messages")
        for idx, msg in enumerate(request.messages):
            logger.info(
                f"  Message {idx}: {msg.role} - "
                f"{msg.content[:50] if msg.content else 'None'}"
            )

        current_prompt, current_tool_results = process_conversation_history(
            request.messages, model, conversation, llm_tools, system_prompt
        )
        logger.info(f"Current prompt after processing: {current_prompt}")
        logger.info(f"Tool results: {len(current_tool_results)}")

        # Prepare options
        options = _prepare_model_options(request)

        # Handle streaming vs non-streaming responses
        if request.stream:
            return StreamingResponse(
                stream_response(
                    conversation,
                    current_prompt or "",
                    system_prompt,
                    options,
                    request.model,
                    llm_tools,
                    current_tool_results if current_tool_results else None,
                    schema,
                    hasattr(model, "supports_tools") and model.supports_tools,
                ),
                media_type="text/event-stream",
            )
        else:
            return _generate_non_streaming_response(
                conversation,
                current_prompt,
                system_prompt,
                options,
                request,
                llm_tools,
                current_tool_results,
                schema,
                model,
            )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        """Log 404 errors to help debug routing issues"""
        logger.warning(f"404 Not Found: {request.method} {request.url.path}")
        logger.warning(f"Available routes: {[str(route) for route in app.routes]}")
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=404, content={"detail": f"Not Found: {request.url.path}"}
        )

    return app


async def stream_response(
    conversation,
    user_prompt: str,
    system_prompt: Optional[str],
    options: Dict[str, Any],
    model_id: str,
    llm_tools: List[llm.Tool],
    tool_results: Optional[List[llm.ToolResult]],
    schema: Optional[Dict[str, Any]],
    supports_tools: bool,
) -> AsyncIterator[str]:
    """Stream the response in OpenAI format"""
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
    created = int(time.time())

    try:
        # Use conversation with history to generate response
        response = conversation.prompt(
            user_prompt,
            system=system_prompt,
            tools=llm_tools,
            tool_results=tool_results,
            schema=schema,
            **options,
        )

        # Stream the response chunks
        collected_text = ""
        for chunk in response:
            collected_text += chunk
            stream_chunk = ChatCompletionStreamResponse(
                id=completion_id,
                created=created,
                model=model_id,
                choices=[
                    ChatCompletionStreamChoice(
                        index=0, delta={"content": chunk}, finish_reason=None
                    )
                ],
            )
            yield f"data: {stream_chunk.model_dump_json()}\n\n"

        # Check for tool calls
        tool_calls = response.tool_calls() if supports_tools else []

        # Send tool calls if any
        if tool_calls:
            for tc in convert_llm_tool_calls_to_openai(tool_calls):
                tool_call_chunk = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model_id,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"tool_calls": [tc]},
                            "finish_reason": None,
                        }
                    ],
                }
                yield f"data: {json.dumps(tool_call_chunk)}\n\n"

        # Send the final chunk with usage info
        final_response = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model_id,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "tool_calls" if tool_calls else "stop",
                }
            ],
        }

        # Add usage information if available
        if hasattr(response, "usage") and callable(response.usage):
            usage_data = response.usage()
            final_response["usage"] = {
                "prompt_tokens": usage_data.input,
                "completion_tokens": usage_data.output,
                "total_tokens": usage_data.input + usage_data.output,
            }

        yield f"data: {json.dumps(final_response)}\n\n"
        yield "data: [DONE]\n\n"

    except Exception:
        # Per OpenAI spec, errors terminate the stream rather than sending error chunks
        # The client will detect the connection drop
        raise

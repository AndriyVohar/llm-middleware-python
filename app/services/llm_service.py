"""LLM service for managing chat interactions and tool calling."""
from typing import Any

from app.config import get_settings
from app.core.constants import MAX_TOOL_ITERATIONS, PROVIDER_DEEPINFRA, PROVIDER_OLLAMA, PROVIDER_OPENAI
from app.core.exceptions import MaxIterationsException, ProviderException
from app.core.logging import get_logger
from app.providers.base import BaseLLMProvider
from app.providers.deepinfra import DeepInfraProvider
from app.providers.ollama import OllamaProvider
from app.providers.openai_provider import OpenAIProvider
from app.schemas.chat import ChatMessage, ChatRequest, ChatResponse, ToolCallInfo
from app.services.prompt_builder import (
    build_system_prompt_with_tools,
    format_tool_result,
    parse_tool_call_from_response,
)
from app.tools import get_registry

logger = get_logger(__name__)
settings = get_settings()


class LLMService:
    """Service for managing LLM interactions and tool calling loop."""

    def __init__(self):
        """Initialize LLM service."""
        self.tool_registry = get_registry()

    def get_provider(self, provider_name: str | None = None) -> BaseLLMProvider:
        """Get LLM provider instance.

        Args:
            provider_name: Name of provider (deepinfra, openai, ollama)

        Returns:
            Provider instance

        Raises:
            ProviderException: If provider is unknown or unavailable
        """
        provider = (provider_name or settings.default_provider).lower()

        if provider == PROVIDER_DEEPINFRA:
            if not settings.is_deepinfra_available:
                raise ProviderException(
                    "DeepInfra provider not configured. Set DEEPINFRA_API_KEY in environment."
                )
            return DeepInfraProvider()

        elif provider == PROVIDER_OPENAI:
            if not settings.is_openai_available:
                raise ProviderException(
                    "OpenAI provider not configured. Set OPENAI_API_KEY in environment."
                )
            return OpenAIProvider()

        elif provider == PROVIDER_OLLAMA:
            return OllamaProvider()

        else:
            raise ProviderException(
                f"Unknown provider: {provider}. "
                f"Available: {PROVIDER_DEEPINFRA}, {PROVIDER_OPENAI}, {PROVIDER_OLLAMA}"
            )

    def _add_system_prompt_if_needed(
        self,
        messages: list[dict[str, Any]],
        tools: list
    ) -> list[dict[str, Any]]:
        """Add system prompt with tool descriptions if not present.

        Args:
            messages: List of message dictionaries
            tools: List of available tools

        Returns:
            Messages list with system prompt prepended if needed
        """
        has_system = any(msg.get("role") == "system" for msg in messages)

        if not has_system and tools:
            system_prompt_text = build_system_prompt_with_tools(tools)
            system_message = {"role": "system", "content": system_prompt_text}
            return [system_message] + messages

        return messages

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Process chat request with tool calling support.

        Implements text-based tool calling loop:
        1. Add system prompt with tool descriptions
        2. Call LLM (without passing tools to API)
        3. Parse response for tool calls in JSON format
        4. Execute tools if found
        5. Add results to context and repeat
        6. Return final response

        Args:
            request: Chat request with messages and configuration

        Returns:
            Chat response with assistant message and tool execution info

        Raises:
            ProviderException: If provider fails
            MaxIterationsException: If max iterations reached
        """
        try:
            # Get provider and model
            provider = self.get_provider(request.provider)
            model = request.model or settings.default_model

            # Get all available tools
            all_tools = self.tool_registry.get_all()

            # Convert messages and add system prompt
            messages = [msg.model_dump() for msg in request.messages]
            messages = self._add_system_prompt_if_needed(messages, all_tools)

            logger.info(
                f"Starting chat - Provider: {request.provider or settings.default_provider}, "
                f"Model: {model}, Tools: {len(all_tools)}"
            )

            if all_tools:
                logger.debug(f"Available tools: {[t.name for t in all_tools]}")

            tool_calls_made: list[ToolCallInfo] = []
            usage = None
            iterations = 0

            # Tool calling loop
            while iterations < MAX_TOOL_ITERATIONS:
                iterations += 1
                logger.debug(f"Iteration {iterations}/{MAX_TOOL_ITERATIONS}")

                # Call LLM without tools (text-based approach)
                response = await provider.chat(
                    messages=messages,
                    tools=None,
                    model=model,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                )

                content = response.get("content", "")
                usage = response.get("usage")

                logger.debug(f"LLM response length: {len(content)} chars")

                # Parse for tool calls
                tool_call = parse_tool_call_from_response(content)

                if not tool_call:
                    # No tool call - final response
                    logger.info(f"Chat completed in {iterations} iterations")

                    return ChatResponse(
                        success=True,
                        message=ChatMessage(role="assistant", content=content),
                        tool_calls_made=tool_calls_made,
                        usage=usage,
                        provider=request.provider or settings.default_provider,
                        model=model,
                    )

                # Tool call detected
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("arguments", {})

                logger.info(f"Tool call: {tool_name} with args: {list(tool_args.keys())}")

                # Add assistant message
                messages.append({"role": "assistant", "content": content})

                # Execute tool
                try:
                    tool = self.tool_registry.get(tool_name)
                    if not tool:
                        error_msg = f"Tool '{tool_name}' not found"
                        logger.error(error_msg)
                        result = {"error": error_msg}
                    else:
                        result = await tool.execute(**tool_args)
                        logger.info(f"Tool '{tool_name}' executed successfully")

                    # Save tool call info
                    tool_calls_made.append(
                        ToolCallInfo(
                            tool=tool_name,
                            arguments=tool_args,
                            result=result
                        )
                    )

                    # Add result to messages
                    result_message = format_tool_result(tool_name, result)
                    messages.append({"role": "user", "content": result_message})

                except Exception as e:
                    logger.exception(f"Error executing tool '{tool_name}'")
                    error_result = {"error": str(e), "type": type(e).__name__}

                    tool_calls_made.append(
                        ToolCallInfo(
                            tool=tool_name,
                            arguments=tool_args,
                            result=error_result
                        )
                    )

                    result_message = format_tool_result(tool_name, error_result)
                    messages.append({"role": "user", "content": result_message})

            # Max iterations reached
            logger.warning(f"Max iterations ({MAX_TOOL_ITERATIONS}) reached")
            raise MaxIterationsException(
                f"Maximum tool calling iterations ({MAX_TOOL_ITERATIONS}) reached",
                details={
                    "iterations": iterations,
                    "tool_calls": len(tool_calls_made),
                }
            )

        except (ProviderException, MaxIterationsException):
            raise

        except Exception as e:
            logger.exception("Unexpected error in chat service")
            raise ProviderException(
                f"Chat service error: {str(e)}",
                details={"error_type": type(e).__name__}
            )
            return ChatResponse(
                success=False,
                message=ChatMessage(
                    role="assistant",
                    content=f"Помилка: {str(e)}",
                ),
                provider=request.provider or settings.default_provider,
                model=request.model or settings.default_model,
            )


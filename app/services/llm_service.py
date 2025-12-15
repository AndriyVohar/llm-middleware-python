import json
import logging

from app.config import settings
from app.providers.deepinfra import DeepInfraProvider
from app.providers.ollama import OllamaProvider
from app.providers.openai_provider import OpenAIProvider
from app.schemas.chat import ChatMessage, ChatResponse, ChatRequest, ToolCallInfo
from app.services.tool_executor import ToolExecutor
from app.services.prompt_builder import (
    build_system_prompt_with_tools,
    parse_tool_call_from_response,
    format_tool_result,
)
from app.tools import get_registry

logger = logging.getLogger(__name__)

# Максимально разрешене кількість iterations в loop
MAX_TOOL_ITERATIONS = 10


class LLMService:
    """Сервіс для управління LLM взаємодією"""

    def __init__(self):
        self.tool_executor = ToolExecutor()
        self.registry = get_registry()

    def get_provider(self, provider_name: str | None = None):
        """Отримати провайдера за назвою"""
        provider = provider_name or settings.default_provider

        if provider.lower() == "deepinfra":
            return DeepInfraProvider()
        elif provider.lower() == "openai":
            return OpenAIProvider()
        elif provider.lower() == "ollama":
            return OllamaProvider()
        else:
            raise ValueError(f"Невідомий провайдер: {provider}")

    def _add_system_prompt_if_needed(
        self, messages: list[dict], tools: list
    ) -> list[dict]:
        """Додає system prompt з описом інструментів якщо його немає"""
        # Перевіряємо чи є вже system prompt
        has_system = any(msg.get("role") == "system" for msg in messages)

        if not has_system and tools:
            system_prompt_text = build_system_prompt_with_tools(tools)
            system_prompt = {"role": "system", "content": system_prompt_text}
            return [system_prompt] + messages

        return messages

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """
        Основний метод для чату з LLM та text-based tool calling

        Логіка:
        1. Отримати провайдера та всі доступні інструменти
        2. Додати system prompt з описом tools у текстовому форматі
        3. Викликати LLM (БЕЗ передачі tools в API)
        4. Парсити відповідь - чи є tool call в JSON форматі
        5. Якщо є tool call - виконати, додати результат, повторити
        6. Повернути фінальну відповідь
        """
        try:
            # 1. Отримати провайдера
            provider = self.get_provider(request.provider)
            model = request.model or settings.default_model

            # 2. Отримати ВСІ доступні інструменти
            all_tools = self.registry.get_all()

            # 3. Конвертувати повідомлення та додати system prompt з описом tools
            messages = [msg.model_dump() for msg in request.messages]
            messages = self._add_system_prompt_if_needed(messages, all_tools)

            logger.info(f"Tools requested by client: {request.tools}")
            logger.info(
                f"Tools available: {[t.name for t in all_tools] if all_tools else []}"
            )
            if all_tools:
                logger.info(f"Using text-based tool calling with {len(all_tools)} tools")
                logger.info(f"System prompt added: {messages[0].get('role') == 'system'}")

            tool_calls_made: list[ToolCallInfo] = []
            iterations = 0
            usage = None

            # 4. Loop для text-based tool calling
            while iterations < MAX_TOOL_ITERATIONS:
                iterations += 1
                logger.info(f"Iteration {iterations}: Calling LLM")

                # Викликати LLM БЕЗ передачі tools в API (text-based approach)
                response = await provider.chat(
                    messages=messages,
                    tools=None,  # НЕ передаємо tools в API!
                    model=model,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                )

                # Отримати content
                content = response.get("content", "")
                usage = response.get("usage", None)

                logger.info(
                    f"LLM Response - Content length: {len(content)}"
                )
                logger.debug(f"LLM Response content: {content[:500]}...")

                # 5. Парсити tool call з відповіді
                tool_call = parse_tool_call_from_response(content)

                if not tool_call:
                    # Немає tool call - це фінальна відповідь
                    logger.info(
                        f"No tool call detected, finishing after {iterations} iterations"
                    )

                    final_message = ChatMessage(
                        role="assistant",
                        content=content,
                    )

                    return ChatResponse(
                        success=True,
                        message=final_message,
                        tool_calls_made=tool_calls_made,
                        usage=usage,
                        provider=request.provider or settings.default_provider,
                        model=model,
                    )

                # 6. Tool call знайдено
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("arguments", {})

                logger.info(f"Tool call detected: {tool_name} with args: {tool_args}")

                # Додати assistant message
                messages.append({"role": "assistant", "content": content})

                # 7. Виконати tool
                try:
                    tool = self.registry.get(tool_name)
                    if not tool:
                        error_msg = f"Інструмент '{tool_name}' не знайдено"
                        logger.error(error_msg)
                        result = {"error": error_msg}
                    else:
                        # Виконати інструмент
                        result = await tool.execute(**tool_args)
                        logger.info(f"Tool executed successfully: {tool_name}")

                    # Зберегти info про tool call
                    tool_calls_made.append(
                        ToolCallInfo(
                            tool=tool_name, arguments=tool_args, result=result
                        )
                    )

                    # 8. Додати результат до messages
                    result_message = format_tool_result(tool_name, result)
                    messages.append({"role": "user", "content": result_message})

                    logger.debug(f"Tool result added to messages: {result_message[:200]}...")

                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {str(e)}", exc_info=True)
                    error_result = {"error": str(e)}
                    tool_calls_made.append(
                        ToolCallInfo(
                            tool=tool_name, arguments=tool_args, result=error_result
                        )
                    )
                    result_message = format_tool_result(tool_name, error_result)
                    messages.append({"role": "user", "content": result_message})

            # Якщо виконано MAX_TOOL_ITERATIONS - повернути помилку
            logger.warning(
                f"Max iterations ({MAX_TOOL_ITERATIONS}) reached, stopping"
            )
            return ChatResponse(
                success=False,
                message=ChatMessage(
                    role="assistant",
                    content=f"Досягнута максимальна кількість ітерацій ({MAX_TOOL_ITERATIONS})",
                ),
                tool_calls_made=tool_calls_made,
                usage=usage,
                provider=request.provider or settings.default_provider,
                model=model,
            )

        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}", exc_info=True)
            return ChatResponse(
                success=False,
                message=ChatMessage(
                    role="assistant",
                    content=f"Помилка: {str(e)}",
                ),
                provider=request.provider or settings.default_provider,
                model=request.model or settings.default_model,
            )


import logging

from openai import AsyncOpenAI

from app.config import settings
from app.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)

# Доступні моделі в OpenAI
OPENAI_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-3.5-turbo",
]


class OpenAIProvider(BaseLLMProvider):
    """Провайдер для OpenAI"""

    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY не встановлено в конфігурації")

        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        **kwargs,
    ) -> dict:
        """Викликати OpenAI API"""
        try:
            model = kwargs.pop("model", "gpt-4o")
            max_tokens = kwargs.pop("max_tokens", None)
            temperature = kwargs.pop("temperature", 0.7)

            # Підготувати параметри
            chat_kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }

            if max_tokens:
                chat_kwargs["max_tokens"] = max_tokens

            if tools:
                chat_kwargs["tools"] = tools
                logger.info(f"OpenAI: Passing {len(tools)} tools to API")

            logger.debug(f"OpenAI API request params: model={model}, temperature={temperature}, "
                        f"tools={'Yes' if tools else 'No'}, messages_count={len(messages)}")

            # Викликати API
            response = await self.client.chat.completions.create(**chat_kwargs)

            # Обробити відповідь
            result = {
                "content": response.choices[0].message.content or "",
                "tool_calls": [],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }

            # Log token usage
            logger.info(
                f"OpenAI token usage - Model: {model}, "
                f"Prompt: {response.usage.prompt_tokens}, "
                f"Completion: {response.usage.completion_tokens}, "
                f"Total: {response.usage.total_tokens}"
            )

            # Обробити tool calls
            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    result["tool_calls"].append({
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    })

            return result

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    def get_available_models(self) -> list[str]:
        """Отримати список доступних моделей"""
        return OPENAI_MODELS


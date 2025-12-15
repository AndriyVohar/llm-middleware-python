import logging

from openai import AsyncOpenAI

from app.config import settings
from app.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """Провайдер для Ollama"""

    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.client = AsyncOpenAI(
            api_key="ollama",  # Ollama не потребує реального ключа
            base_url=f"{self.base_url}/v1",
        )

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        **kwargs,
    ) -> dict:
        """Викликати Ollama API"""
        try:
            model = kwargs.pop("model", "llama2")
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
                logger.info(f"Ollama: Passing {len(tools)} tools to API")

            logger.debug(f"Ollama API request params: model={model}, temperature={temperature}, "
                        f"tools={'Yes' if tools else 'No'}, messages_count={len(messages)}")

            # Викликати API
            response = await self.client.chat.completions.create(**chat_kwargs)

            # Обробити відповідь
            result = {
                "content": response.choices[0].message.content or "",
                "tool_calls": [],
                "usage": {
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(response.usage, "completion_tokens", 0),
                    "total_tokens": getattr(response.usage, "total_tokens", 0),
                },
            }

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
            logger.error(f"Ollama API error: {str(e)}")
            raise

    def get_available_models(self) -> list[str]:
        """Динамічно отримати список моделей з Ollama"""
        # Ollama моделі отримуються через окремий вызов, поки що повертаємо порожній список
        return []


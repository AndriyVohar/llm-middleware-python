from abc import ABC, abstractmethod



class BaseLLMProvider(ABC):
    """Базовий клас для провайдерів LLM"""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        **kwargs,
    ) -> dict:
        """
        Викликати LLM з повідомленнями та інструментами

        Повинна повертати dict з:
        - content: str - текст відповіді
        - tool_calls: list[dict] - список tool calls (якщо є)
        - usage: dict - інформація про використання токенів
        """
        pass

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Отримати список доступних моделей"""
        pass

    def format_tools(self, tools: list) -> list[dict]:
        """Конвертація інструментів в OpenAI format"""
        return [tool.to_openai_format() for tool in tools]


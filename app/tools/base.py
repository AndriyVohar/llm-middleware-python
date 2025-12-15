from abc import ABC, abstractmethod
from typing import Any

from app.schemas.tools import ToolParameter, ToolSchema


class BaseTool(ABC):
    """Базовий клас для всіх інструментів"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Унікальний ідентифікатор інструмента"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Опис для LLM"""
        pass

    @property
    @abstractmethod
    def parameters(self) -> list[ToolParameter]:
        """Параметри інструмента"""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Виконати інструмент"""
        pass

    def get_schema(self) -> ToolSchema:
        """Повернути схему інструмента"""
        return ToolSchema(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
        )

    def to_openai_format(self) -> dict:
        """Конвертувати в OpenAI tool format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        param.name: {
                            "type": param.type,
                            "description": param.description,
                        }
                        for param in self.parameters
                    },
                    "required": [
                        param.name for param in self.parameters if param.required
                    ],
                },
            },
        }


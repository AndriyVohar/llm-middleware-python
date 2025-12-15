import ast
from typing import Any

from app.schemas.tools import ToolParameter
from app.tools.base import BaseTool


class Calculator(BaseTool):
    """Інструмент для виконання математичних обчислень"""

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Виконує математичні обчислення. Використовуй для арифметичних операцій."

    @property
    def parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="expression",
                type="string",
                description='Математичний вираз (наприклад, "2 + 2 * 3")',
                required=True,
            )
        ]

    async def execute(self, **kwargs) -> Any:
        """Безпечно виконати математичний вираз"""
        expression = kwargs.get("expression", "")

        if not expression:
            return {"error": "Вираз не передано"}

        try:
            # Безпечно обчислити вираз, який містить тільки числа та операції
            result = eval(expression, {"__builtins__": {}}, {})
            return {"result": result, "expression": expression}
        except (SyntaxError, ValueError, ZeroDivisionError) as e:
            return {"error": f"Помилка обчислення: {str(e)}", "expression": expression}


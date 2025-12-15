import json
import logging
from typing import Any

from app.tools import get_registry

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Сервіс для виконання tool calls"""

    async def execute_tool_calls(self, tool_calls: list[dict]) -> list[dict]:
        """
        Виконати список tool calls

        Args:
            tool_calls: список dict з полями:
                - id: str - унікальний ID
                - name: str - назва інструмента
                - arguments: str | dict - JSON строка або dict

        Returns:
            список dict з полями:
                - tool_call_id: str
                - tool_name: str
                - result: Any
                - error: str | None
        """
        results = []
        registry = get_registry()

        for tool_call in tool_calls:
            tool_call_id = tool_call.get("id", "unknown")
            tool_name = tool_call.get("name", "")
            arguments = tool_call.get("arguments", {})

            logger.info(f"Executing tool: {tool_name} with args: {arguments}")

            # Обробити аргументи (можуть бути JSON строкою)
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse arguments for {tool_name}")
                    results.append({
                        "tool_call_id": tool_call_id,
                        "tool_name": tool_name,
                        "result": None,
                        "error": "Помилка парсингу аргументів",
                    })
                    continue

            # Отримати інструмент
            tool = registry.get(tool_name)
            if not tool:
                logger.error(f"Tool not found: {tool_name}")
                results.append({
                    "tool_call_id": tool_call_id,
                    "tool_name": tool_name,
                    "result": None,
                    "error": f"Інструмент '{tool_name}' не знайдено",
                })
                continue

            # Виконати інструмент
            try:
                result = await tool.execute(**arguments)
                results.append({
                    "tool_call_id": tool_call_id,
                    "tool_name": tool_name,
                    "result": result,
                    "error": None,
                })
                logger.info(f"Tool executed successfully: {tool_name}")
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {str(e)}")
                results.append({
                    "tool_call_id": tool_call_id,
                    "tool_name": tool_name,
                    "result": None,
                    "error": str(e),
                })

        return results


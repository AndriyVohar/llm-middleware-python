"""
Побудова промптів з описом доступних інструментів для text-based tool calling
"""
import json
from typing import Any

from app.tools.base import BaseTool


def build_tools_prompt(tools: list[BaseTool]) -> str:
    """
    Створює текстовий опис інструментів для додавання в system prompt

    Args:
        tools: список доступних інструментів

    Returns:
        Текстовий опис інструментів у форматі для промпту
    """
    if not tools:
        return ""

    tools_description = []
    tools_description.append("## ДОСТУПНІ ІНСТРУМЕНТИ (TOOLS)\n")
    tools_description.append("Ти маєш доступ до наступних інструментів:\n")

    for tool in tools:
        tools_description.append(f"\n### {tool.name}")
        tools_description.append(f"Опис: {tool.description}")
        tools_description.append("Параметри:")

        for param in tool.parameters:
            required = "обов'язковий" if param.required else "опціональний"
            tools_description.append(f"  - {param.name} ({param.type}, {required}): {param.description}")

    tools_description.append("\n## ЯК ВИКОРИСТОВУВАТИ ІНСТРУМЕНТИ\n")
    tools_description.append(
        "Щоб використати інструмент, поверни JSON у своїй відповіді у форматі:\n"
        "```json\n"
        "{\n"
        '  "tool_call": {\n'
        '    "name": "назва_інструмента",\n'
        '    "arguments": {\n'
        '      "параметр1": "значення1",\n'
        '      "параметр2": "значення2"\n'
        "    }\n"
        "  }\n"
        "}\n"
        "```\n"
    )

    tools_description.append("\n## ВАЖЛИВІ ПРАВИЛА:\n")
    tools_description.append("1. Якщо потрібен точний розрахунок - використовуй calculator\n")
    tools_description.append("2. Якщо потрібна актуальна інформація - використовуй web_search або news_search\n")
    tools_description.append("3. Якщо потрібен контент сайту - використовуй web_scraper\n")
    tools_description.append("4. Поверни ТІЛЬКИ JSON з tool_call, без додаткового тексту\n")
    tools_description.append("5. Після отримання результату від інструмента, надай користувачу зрозумілу відповідь\n")
    tools_description.append("6. Якщо питання просте і не потребує інструментів - відповідай безпосередньо\n")

    return "\n".join(tools_description)


def build_system_prompt_with_tools(tools: list[BaseTool]) -> str:
    """
    Створює повний system prompt з описом інструментів

    Args:
        tools: список доступних інструментів

    Returns:
        Повний system prompt
    """
    base_prompt = (
        "Ти - розумний AI асистент з доступом до інструментів.\n"
        "Твоя задача - допомагати користувачам, використовуючи доступні інструменти коли це необхідно.\n"
    )

    if tools:
        tools_prompt = build_tools_prompt(tools)
        return f"{base_prompt}\n{tools_prompt}"

    return base_prompt


def parse_tool_call_from_response(response_text: str) -> dict[str, Any] | None:
    """
    Парсить tool call з текстової відповіді моделі

    Args:
        response_text: текст відповіді від моделі

    Returns:
        dict з tool call або None якщо не знайдено
        Формат: {"name": "tool_name", "arguments": {...}}
    """
    if not response_text:
        return None

    # Шукаємо JSON блок з tool_call
    try:
        # Спроба 1: Парсити весь текст як JSON
        data = json.loads(response_text.strip())
        if "tool_call" in data:
            return data["tool_call"]
    except json.JSONDecodeError:
        pass

    # Спроба 2: Шукаємо JSON в markdown блоках
    import re

    # Шукаємо ```json ... ``` блоки
    json_blocks = re.findall(r'```json\s*(\{.*?})\s*```', response_text, re.DOTALL)
    for block in json_blocks:
        try:
            data = json.loads(block)
            if "tool_call" in data:
                return data["tool_call"]
        except json.JSONDecodeError:
            continue

    # Спроба 3: Шукаємо будь-які JSON об'єкти в тексті
    json_objects = re.findall(r'\{[^{}]*"tool_call"[^{}]*\{[^}]*}[^}]*}', response_text, re.DOTALL)
    for obj in json_objects:
        try:
            data = json.loads(obj)
            if "tool_call" in data:
                return data["tool_call"]
        except json.JSONDecodeError:
            continue

    return None


def format_tool_result(tool_name: str, result: Any) -> str:
    """
    Форматує результат виконання інструмента для повернення моделі

    Args:
        tool_name: назва інструмента
        result: результат виконання

    Returns:
        Форматований текст з результатом
    """
    result_text = (
        f"Результат виконання інструмента '{tool_name}':\n"
        f"```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```\n"
        f"\nТепер використай цей результат для формування відповіді користувачу."
    )
    return result_text


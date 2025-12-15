"""Prompt building utilities for text-based tool calling."""
import json
import re
from typing import Any

from app.core.logging import get_logger
from app.tools.base import BaseTool

logger = get_logger(__name__)


def build_tools_prompt(tools: list[BaseTool]) -> str:
    """Create textual description of tools for system prompt.

    Args:
        tools: List of available tool objects

    Returns:
        Formatted text description of tools and usage instructions
    """
    if not tools:
        return ""

    lines = [
        "## ДОСТУПНІ ІНСТРУМЕНТИ (TOOLS)\n",
        "Ти маєш доступ до наступних інструментів:\n"
    ]

    for tool in tools:
        lines.append(f"\n### {tool.name}")
        lines.append(f"Опис: {tool.description}")
        lines.append("Параметри:")

        for param in tool.parameters:
            required = "обов'язковий" if param.required else "опціональний"
            lines.append(
                f"  - {param.name} ({param.type}, {required}): {param.description}"
            )

    lines.extend([
        "\n## ЯК ВИКОРИСТОВУВАТИ ІНСТРУМЕНТИ\n",
        "Щоб використати інструмент, поверни JSON у своїй відповіді у форматі:\n",
        "```json\n",
        "{\n",
        '  "tool_call": {\n',
        '    "name": "назва_інструмента",\n',
        '    "arguments": {\n',
        '      "параметр1": "значення1",\n',
        '      "параметр2": "значення2"\n',
        "    }\n",
        "  }\n",
        "}\n",
        "```\n",
        "\n## ВАЖЛИВІ ПРАВИЛА:\n",
        "1. Якщо потрібен точний розрахунок - використовуй calculator\n",
        "2. Якщо потрібна актуальна інформація - використовуй web_search або news_search\n",
        "3. Якщо потрібен контент сайту - використовуй web_scraper\n",
        "4. Поверни ТІЛЬКИ JSON з tool_call, без додаткового тексту\n",
        "5. Після отримання результату від інструмента, надай користувачу зрозумілу відповідь\n",
        "6. Якщо питання просте і не потребує інструментів - відповідай безпосередньо\n"
    ])

    return "\n".join(lines)


def build_system_prompt_with_tools(tools: list[BaseTool]) -> str:
    """Create complete system prompt with tool descriptions.

    Args:
        tools: List of available tool objects

    Returns:
        Complete system prompt text
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
    """Parse tool call from LLM response text.

    Tries multiple strategies to extract tool call JSON:
    1. Parse entire response as JSON
    2. Extract JSON from markdown code blocks
    3. Find JSON objects containing "tool_call"

    Args:
        response_text: Text response from LLM

    Returns:
        Tool call dictionary with 'name' and 'arguments', or None if not found
    """
    if not response_text:
        return None

    # Strategy 1: Parse entire text as JSON
    try:
        data = json.loads(response_text.strip())
        if "tool_call" in data:
            logger.debug("Found tool call in direct JSON parse")
            return data["tool_call"]
    except json.JSONDecodeError:
        pass

    # Strategy 2: Extract from markdown JSON blocks
    json_blocks = re.findall(
        r'```json\s*(\{.*?})\s*```',
        response_text,
        re.DOTALL
    )
    for block in json_blocks:
        try:
            data = json.loads(block)
            if "tool_call" in data:
                logger.debug("Found tool call in markdown block")
                return data["tool_call"]
        except json.JSONDecodeError:
            continue

    # Strategy 3: Find any JSON object with "tool_call"
    json_objects = re.findall(
        r'\{[^{}]*"tool_call"[^{}]*\{[^}]*}[^}]*}',
        response_text,
        re.DOTALL
    )
    for obj in json_objects:
        try:
            data = json.loads(obj)
            if "tool_call" in data:
                logger.debug("Found tool call in inline JSON")
                return data["tool_call"]
        except json.JSONDecodeError:
            continue

    logger.debug("No tool call found in response")
    return None


def format_tool_result(tool_name: str, result: Any) -> str:
    """Format tool execution result for returning to LLM.

    Args:
        tool_name: Name of executed tool
        result: Tool execution result (any JSON-serializable data)

    Returns:
        Formatted message with tool result
    """
    result_text = (
        f"Результат виконання інструмента '{tool_name}':\n"
        f"```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```\n"
        f"\nТепер використай цей результат для формування відповіді користувачу."
    )
    return result_text




"""Test prompt builder utilities."""
from app.services.prompt_builder import (
    build_system_prompt_with_tools,
    build_tools_prompt,
    format_tool_result,
    parse_tool_call_from_response,
)
from app.tools import get_registry


def test_build_tools_prompt():
    """Test tools prompt generation."""
    registry = get_registry()
    tools = registry.get_all()

    prompt = build_tools_prompt(tools)
    assert "ДОСТУПНІ ІНСТРУМЕНТИ" in prompt
    assert "ЯК ВИКОРИСТОВУВАТИ" in prompt
    assert "tool_call" in prompt


def test_build_system_prompt_with_tools():
    """Test system prompt generation."""
    registry = get_registry()
    tools = registry.get_all()

    prompt = build_system_prompt_with_tools(tools)
    assert "AI асистент" in prompt
    assert "ІНСТРУМЕНТИ" in prompt


def test_parse_tool_call_json():
    """Test parsing tool call from JSON response."""
    response = '''
    {
        "tool_call": {
            "name": "calculator",
            "arguments": {"expression": "2 + 2"}
        }
    }
    '''
    result = parse_tool_call_from_response(response)
    assert result is not None
    assert result["name"] == "calculator"
    assert result["arguments"]["expression"] == "2 + 2"


def test_parse_tool_call_markdown():
    """Test parsing tool call from markdown code block."""
    response = '''
    ```json
    {
        "tool_call": {
            "name": "web_search",
            "arguments": {"query": "test"}
        }
    }
    ```
    '''
    result = parse_tool_call_from_response(response)
    assert result is not None
    assert result["name"] == "web_search"


def test_parse_no_tool_call():
    """Test parsing when no tool call present."""
    response = "Just a regular response without tool calls."
    result = parse_tool_call_from_response(response)
    assert result is None


def test_format_tool_result():
    """Test formatting tool result."""
    result = {"answer": 42}
    formatted = format_tool_result("calculator", result)
    assert "calculator" in formatted
    assert "42" in formatted
    assert "Результат виконання" in formatted


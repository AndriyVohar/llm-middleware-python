from typing import Any, Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    tool_call_id: str | None = None
    name: str | None = None


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    provider: str | None = None  # deepinfra, openai, ollama
    model: str | None = None
    tools: list[str] = []  # ["web_search", "calculator"]
    stream: bool = False
    max_tokens: int | None = None
    temperature: float = 0.7


class ToolCallInfo(BaseModel):
    tool: str
    arguments: dict
    result: Any


class ChatResponse(BaseModel):
    success: bool
    message: ChatMessage
    tool_calls_made: list[ToolCallInfo] = []
    usage: dict | None = None
    provider: str
    model: str


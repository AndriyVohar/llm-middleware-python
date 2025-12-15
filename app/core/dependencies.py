"""FastAPI dependencies."""
from functools import lru_cache

from app.config import Settings
from app.services.llm_service import LLMService
from app.tools import ToolRegistry, get_registry


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()


def get_llm_service() -> LLMService:
    """Get LLM service instance."""
    return LLMService()


def get_tool_registry() -> ToolRegistry:
    """Get tool registry instance."""
    return get_registry()


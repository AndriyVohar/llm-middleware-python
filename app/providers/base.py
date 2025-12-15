"""Base class for LLM providers."""
from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers.

    All provider implementations should inherit from this class
    and implement the required methods.
    """

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        **kwargs,
    ) -> dict[str, Any]:
        """Send chat request to LLM provider.

        Args:
            messages: List of chat messages with role and content
            tools: Optional list of tool definitions
            model: Model identifier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters

        Returns:
            Response dictionary with:
                - content: str - Response text
                - tool_calls: list[dict] - Tool calls if any
                - usage: dict - Token usage information

        Raises:
            ProviderException: If provider request fails
        """
        pass

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Get list of available models for this provider.

        Returns:
            List of model identifiers
        """
        pass

    def format_tools(self, tools: list) -> list[dict[str, Any]]:
        """Convert tool objects to provider-specific format.

        Args:
            tools: List of tool objects

        Returns:
            List of tool definitions in provider format
        """
        if not tools:
            return []
        return [tool.to_openai_format() for tool in tools]




"""Custom exceptions for the application."""


class LLMMiddlewareException(Exception):
    """Base exception for LLM middleware."""

    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ProviderException(LLMMiddlewareException):
    """Exception raised when provider encounters an error."""

    pass


class ToolExecutionException(LLMMiddlewareException):
    """Exception raised when tool execution fails."""

    pass


class ConfigurationException(LLMMiddlewareException):
    """Exception raised for configuration errors."""

    pass


class ValidationException(LLMMiddlewareException):
    """Exception raised for validation errors."""

    pass


class MaxIterationsException(LLMMiddlewareException):
    """Exception raised when max iterations reached."""

    pass


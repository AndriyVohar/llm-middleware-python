"""Application configuration."""
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import (
    DEFAULT_MAX_CONCURRENT_REQUESTS,
    DEFAULT_MODEL_DEEPINFRA,
    DEFAULT_SEARCH_REGION,
    DEFAULT_SEARCH_RESULTS,
    DEFAULT_USER_AGENT,
    DEFAULT_WEB_TIMEOUT,
    MAX_SEARCH_RESULTS,
    PROVIDER_DEEPINFRA,
)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    # API Keys
    deepinfra_api_key: str | None = Field(None, description="DeepInfra API key")
    openai_api_key: str | None = Field(None, description="OpenAI API key")

    # Provider settings
    ollama_base_url: str = Field(
        "http://localhost:11434",
        description="Ollama base URL"
    )
    default_provider: Literal["deepinfra", "openai", "ollama"] = Field(
        PROVIDER_DEEPINFRA,
        description="Default LLM provider"
    )
    default_model: str = Field(
        DEFAULT_MODEL_DEEPINFRA,
        description="Default model for provider"
    )

    # Web scraping settings
    web_scraping_enabled: bool = Field(True, description="Enable web scraping")
    web_scraping_timeout: int = Field(DEFAULT_WEB_TIMEOUT, description="Web scraping timeout in seconds")
    web_scraping_max_concurrent: int = Field(DEFAULT_MAX_CONCURRENT_REQUESTS, description="Max concurrent requests")
    web_scraping_user_agent: str = Field(DEFAULT_USER_AGENT, description="User agent for web scraping")

    # Search settings
    default_search_region: str = Field(DEFAULT_SEARCH_REGION, description="Default search region")
    default_search_results: int = Field(DEFAULT_SEARCH_RESULTS, description="Default number of search results")
    max_search_results: int = Field(MAX_SEARCH_RESULTS, description="Maximum search results")

    # Logging
    log_level: str = Field("INFO", description="Logging level")

    @property
    def is_deepinfra_available(self) -> bool:
        """Check if DeepInfra is configured."""
        return self.deepinfra_api_key is not None

    @property
    def is_openai_available(self) -> bool:
        """Check if OpenAI is configured."""
        return self.openai_api_key is not None

    @property
    def is_ollama_available(self) -> bool:
        """Ollama is always available if running locally."""
        return True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance (for backward compatibility)
settings = get_settings()



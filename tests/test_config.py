"""Test configuration module."""
from app.config import Settings, get_settings


def test_settings_defaults():
    """Test default settings values."""
    settings = Settings()
    assert settings.default_provider in ["deepinfra", "openai", "ollama"]
    assert settings.web_scraping_enabled is True
    assert settings.log_level == "INFO"


def test_get_settings_cached():
    """Test that get_settings returns cached instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2


def test_provider_availability():
    """Test provider availability properties."""
    settings = Settings()
    # Ollama is always available
    assert settings.is_ollama_available is True


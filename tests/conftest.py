"""Test configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_chat_request():
    """Sample chat request for testing."""
    return {
        "messages": [
            {"role": "user", "content": "Hello!"}
        ],
        "provider": "ollama",
        "model": "qwen2.5:7b",
    }


@pytest.fixture
def sample_tool_request():
    """Sample chat request with tools."""
    return {
        "messages": [
            {"role": "user", "content": "Calculate 2 + 2"}
        ],
        "provider": "ollama",
        "tools": ["calculator"],
    }


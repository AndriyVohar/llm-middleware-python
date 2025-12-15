"""Test main application endpoints."""
import pytest


def test_root_endpoint(client):
    """Test root endpoint returns correct response."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "LLM Middleware"
    assert data["status"] == "running"


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "config" in data
    assert "default_provider" in data["config"]


def test_providers_list(client):
    """Test providers endpoint returns list of providers."""
    response = client.get("/api/providers")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert len(data["providers"]) >= 3

    # Check provider structure
    provider_names = [p["name"] for p in data["providers"]]
    assert "deepinfra" in provider_names
    assert "openai" in provider_names
    assert "ollama" in provider_names


def test_tools_list(client):
    """Test tools endpoint returns list of tools."""
    response = client.get("/api/tools")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Check tool structure
    tool = data[0]
    assert "name" in tool
    assert "description" in tool
    assert "parameters" in tool


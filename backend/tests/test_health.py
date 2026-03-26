"""Tests for health endpoint."""
import pytest


@pytest.mark.asyncio
async def test_health_returns_200(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "llm_provider" in data
    assert "agent_enabled" in data
    assert "reranker_enabled" in data


@pytest.mark.asyncio
async def test_health_has_request_id(client):
    response = await client.get("/health")
    assert "x-request-id" in response.headers


@pytest.mark.asyncio
async def test_health_echoes_request_id(client):
    custom_id = "test-health-123"
    response = await client.get("/health", headers={"X-Request-ID": custom_id})
    assert response.headers.get("x-request-id") == custom_id

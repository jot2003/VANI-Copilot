"""Tests for API key authentication."""
import pytest


@pytest.mark.asyncio
async def test_chat_requires_api_key(client):
    response = await client.post("/api/chat", json={"message": "hello"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_chat_rejects_wrong_key(client):
    response = await client.post(
        "/api/chat",
        json={"message": "hello"},
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_conversations_require_api_key(client):
    response = await client.get("/api/conversations")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_analytics_require_api_key(client):
    response = await client.get("/api/analytics/overview")
    assert response.status_code == 401

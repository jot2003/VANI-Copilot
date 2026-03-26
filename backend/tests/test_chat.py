"""Tests for chat endpoints."""
import pytest


@pytest.mark.asyncio
async def test_chat_validates_empty_message(client, api_headers):
    response = await client.post("/api/chat", json={"message": ""}, headers=api_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_validates_too_long_message(client, api_headers):
    response = await client.post(
        "/api/chat",
        json={"message": "x" * 2001},
        headers=api_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_returns_reply(client, api_headers):
    response = await client.post(
        "/api/chat",
        json={"message": "Xin chao"},
        headers=api_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "conversation_id" in data
    assert isinstance(data["sources"], list)


@pytest.mark.asyncio
async def test_chat_creates_conversation(client, api_headers):
    response = await client.post(
        "/api/chat",
        json={"message": "test conversation"},
        headers=api_headers,
    )
    data = response.json()
    conv_id = data["conversation_id"]
    assert conv_id is not None

    conv_response = await client.get(f"/api/conversations/{conv_id}", headers=api_headers)
    assert conv_response.status_code == 200
    conv_data = conv_response.json()
    assert len(conv_data["messages"]) >= 2


@pytest.mark.asyncio
async def test_chat_stream_returns_sse(client, api_headers):
    response = await client.post(
        "/api/chat/stream",
        json={"message": "test stream"},
        headers={**api_headers, "Accept": "text/event-stream"},
    )
    assert response.status_code == 200
    assert "data:" in response.text

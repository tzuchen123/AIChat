from unittest.mock import AsyncMock, patch

import pytest


async def _setup(client, suffix=""):
    await client.post(
        "/api/auth/register",
        json={
            "username": f"msguser{suffix}",
            "email": f"msguser{suffix}@example.com",
            "password": "password",
        },
    )
    resp = await client.post(
        "/api/auth/login",
        json={"email": f"msguser{suffix}@example.com", "password": "password"},
    )
    token = resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    conv_resp = await client.post(
        "/api/chat/", json={"title": "Test Chat"}, headers=headers
    )
    conv_id = conv_resp.json()["data"]["id"]
    return headers, conv_id


@pytest.mark.asyncio
async def test_list_messages_empty(client):
    headers, conv_id = await _setup(client, "1")
    resp = await client.get(f"/api/messages/{conv_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["data"]["messages"] == []
    assert resp.json()["data"]["total"] == 0


@pytest.mark.asyncio
async def test_send_message(client):
    headers, conv_id = await _setup(client, "2")

    async def fake_stream(messages):
        yield "Hello"
        yield " World"

    with patch(
        "src.services.openai_service.OpenAIService.stream_response",
        return_value=fake_stream([]),
    ):
        resp = await client.post(
            f"/api/messages/{conv_id}",
            json={"content": "Hi"},
            headers=headers,
        )

    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["role"] == "assistant"
    assert data["content"] == "Hello World"


@pytest.mark.asyncio
async def test_send_message_to_others_conversation(client):
    headers1, conv_id = await _setup(client, "3")

    await client.post(
        "/api/auth/register",
        json={"username": "other", "email": "other@example.com", "password": "password"},
    )
    login_resp = await client.post(
        "/api/auth/login",
        json={"email": "other@example.com", "password": "password"},
    )
    headers2 = {"Authorization": f"Bearer {login_resp.json()['data']['access_token']}"}

    resp = await client.post(
        f"/api/messages/{conv_id}",
        json={"content": "Hacking"},
        headers=headers2,
    )
    assert resp.status_code == 403

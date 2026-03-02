import pytest


async def _register_and_login(client, suffix=""):
    await client.post(
        "/api/auth/register",
        json={
            "username": f"chatuser{suffix}",
            "email": f"chatuser{suffix}@example.com",
            "password": "password",
        },
    )
    resp = await client.post(
        "/api/auth/login",
        json={"email": f"chatuser{suffix}@example.com", "password": "password"},
    )
    return resp.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_create_and_list_conversation(client):
    token = await _register_and_login(client, "1")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/chat/", json={"title": "My Chat"}, headers=headers
    )
    assert create_resp.status_code == 201
    assert create_resp.json()["data"]["title"] == "My Chat"

    list_resp = await client.get("/api/chat/", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()["data"]) == 1


@pytest.mark.asyncio
async def test_delete_conversation(client):
    token = await _register_and_login(client, "2")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/chat/", json={"title": "To Delete"}, headers=headers
    )
    conv_id = create_resp.json()["data"]["id"]

    delete_resp = await client.delete(f"/api/chat/{conv_id}", headers=headers)
    assert delete_resp.status_code == 200

    list_resp = await client.get("/api/chat/", headers=headers)
    assert list_resp.json()["data"] == []


@pytest.mark.asyncio
async def test_unauthorized_access(client):
    response = await client.get("/api/chat/")
    assert response.status_code == 403

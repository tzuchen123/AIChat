import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "secret"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == "test@example.com"
    assert body["data"]["username"] == "testuser"


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    await client.post(
        "/api/auth/register",
        json={"username": "user1", "email": "dup@example.com", "password": "pass"},
    )
    response = await client.post(
        "/api/auth/register",
        json={"username": "user2", "email": "dup@example.com", "password": "pass"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post(
        "/api/auth/register",
        json={"username": "loginuser", "email": "login@example.com", "password": "mypassword"},
    )
    response = await client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "mypassword"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "access_token" in body["data"]


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post(
        "/api/auth/register",
        json={"username": "wrongpw", "email": "wrongpw@example.com", "password": "correct"},
    )
    response = await client.post(
        "/api/auth/login",
        json={"email": "wrongpw@example.com", "password": "wrong"},
    )
    assert response.status_code == 401

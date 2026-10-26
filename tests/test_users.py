
from httpx import AsyncClient


async def test_create_user_returns_201(client: AsyncClient):
    response = await client.post(
        "/users",
        json={
            "email": "new@example.com",
            "name": "New User",
        },
    )

    assert response.status_code == 201

    body = response.json()
    assert body["email"] == "new@example.com"
    assert body["name"] == "New User"
    assert isinstance(body["id"], int)


async def test_duplicate_email_returns_409(client: AsyncClient):
    payload = {
        "email": "duplicate@example.com",
        "name": "First User",
    }

    first = await client.post("/users", json=payload)
    second = await client.post(
        "/users",
        json={
            "email": payload["email"],
            "name": "Second User",
        },
    )

    assert first.status_code == 201
    assert second.status_code == 409


async def test_invalid_email_returns_422(client: AsyncClient):
    response = await client.post(
        "/users",
        json={
            "email": "not-an-email",
            "name": "Invalid User",
        },
    )

    assert response.status_code == 422

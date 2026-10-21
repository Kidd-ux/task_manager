import pytest
from conftest import TestSessionLocal
from sqlalchemy import select
from models import User


def test_get_all_users(client):
    response = client.get("/users")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_user_by_id(client):
    data = {
        "username": "Bob",
        "age": 18,
        "email": "bob@test.com",
        "password": "password_1s",
    }
    user_data = client.post("/users", json=data)
    response = client.get(f"/users/{user_data.json()['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["username"] == "Bob"
    assert response.json()["email"] == "bob@test.com"
    assert response.json()["age"] == 18


def test_get_user_not_found(client):
    response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.parametrize("missing_field", ["username", "age", "email", "password"])
def test_create_user_missing_field(client, missing_field):
    data = {
        "username": "Bob",
        "age": 18,
        "email": "bob@test.com",
        "password": "password_1s",
    }
    del data[missing_field]
    response = client.post("/users", json=data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", missing_field]


@pytest.mark.parametrize("invalid_age", ["abc", -1])
def test_create_user_invalid_age(client, invalid_age):
    data = {
        "username": "Bob",
        "age": invalid_age,
        "email": "bob@test.com",
        "password": "password_1s",
    }
    response = client.post("/users", json=data)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "age"]


def test_create_user(client):
    data = {
        "username": "Bob",
        "age": 18,
        "email": "bob@test.com",
        "password": "password_1s",
    }
    response = client.post("/users", json=data)
    assert response.status_code == 200
    assert response.json()["username"] == "Bob"
    assert response.json()["age"] == 18
    assert response.json()["email"] == "bob@test.com"
    assert "password" not in response.json()


def test_email_already_exists(client):
    data = {
        "username": "Bob",
        "age": 18,
        "email": "bob@test.com",
        "password": "password_1s",
    }
    invalid_data = {
        "username": "Alex",
        "age": 11,
        "email": "bob@test.com",
        "password": "password_2s",
    }
    created = client.post("/users", json=data)
    assert created.status_code == 200
    response = client.post("/users", json=invalid_data)
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already exists"


@pytest.mark.asyncio
async def test_hash_password(client):
    data = {
        "username": "Bob",
        "age": 18,
        "email": "bob@test.com",
        "password": "password_1s",
    }
    client.post("/users", json=data)
    async with TestSessionLocal() as db:
        res = await db.execute(select(User).where(User.username == "Bob"))
        res = res.scalar_one_or_none()
    assert res is not None
    assert res.password_hash is not None
    assert res.password_hash != data["password"]


def test_patch_users_age(client, auth_headers):
    response = client.patch("/users/me", json={"age": -1}, headers=auth_headers)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "age"]

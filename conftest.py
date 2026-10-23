import os

os.environ["REDIS_DB"] = "1"
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from main import app
from db import get_db, Base
import models
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from fastapi.testclient import TestClient
import redis
from config import TEST_DATABASE_URL

if TEST_DATABASE_URL is None or not TEST_DATABASE_URL.endswith("_test"):
    raise ValueError("TEST_DATABASE_URL is not correct, please check URL")

test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as db:
        yield db


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def clean_test_db():
    async with test_engine.begin() as conn:
        await conn.execute(
            text(
                "TRUNCATE TABLE comments, tasks, projects, users RESTART IDENTITY CASCADE"
            )
        )
        redis_client = redis.Redis(
            host="127.0.0.1", port=6379, decode_responses=True, db=1
        )
    redis_client.flushdb()
    redis_client.close()


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def user_data():
    return {
        "username": "Bob",
        "age": 18,
        "email": "bob@test.com",
        "password": "password_1s",
    }


@pytest.fixture
def user_data_2():
    return {
        "username": "John",
        "age": 19,
        "email": "john@test.com",
        "password": "password_2s",
    }


@pytest.fixture
def project_create(client, auth_headers):
    project = client.post(
        "/projects", json={"name": "test_project"}, headers=auth_headers
    )
    assert project.status_code == 200
    return project.json()


@pytest.fixture
def task_data(project_create):
    return {
        "title": "test_task",
        "description": "empty",
        "status": "todo",
        "project_id": int(project_create["id"]),
    }


@pytest.fixture
def task_create(client, task_data, auth_headers):
    task = client.post("/tasks", json=task_data, headers=auth_headers)
    assert task.status_code == 200
    return task.json()


@pytest.fixture
def comment_data(task_create):
    return {"text": "test_comment", "task_id": task_create["id"]}


@pytest.fixture
def comment_create(client, comment_data, auth_headers):
    comment = client.post("/comments", json=comment_data, headers=auth_headers)
    assert comment.status_code == 200
    return comment.json()


@pytest.fixture
def user(client, user_data):
    response = client.post("/users", json=user_data)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def auth_headers(
    client, user, user_data
):  # user тут как просто вызов - а если вызвалось значит выполнилось => создало юзера
    response = client.post(
        "/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    assert response.status_code == 200
    token = response.json()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def make_headers(client):
    def _make(data):
        response = client.post("/users", json=data)
        assert response.status_code == 200

        response = client.post(
            "/auth/login",
            json={"email": data["email"], "password": data["password"]},
        )
        assert response.status_code == 200
        token = response.json()
        return {"Authorization": f"Bearer {token}"}

    return _make

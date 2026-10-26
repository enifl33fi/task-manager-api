import os
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db import get_session
from app.main import app
from app.models import Base

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/tasks_test",
)

test_engine = create_async_engine(TEST_DATABASE_URL)

TestSession = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(autouse=True)
async def clean_database():
    # Работает только с TEST_DATABASE_URL.
    # Перед каждым тестом пересоздаёт таблицы.
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    yield

    # Удаляем данные после теста.
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_session, None)


@pytest_asyncio.fixture
async def user(client: AsyncClient) -> dict:
    response = await client.post(
        "/users",
        json={
            "email": "owner@example.com",
            "name": "Test Owner",
        },
    )

    assert response.status_code == 201
    return response.json()

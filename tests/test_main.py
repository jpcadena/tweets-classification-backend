"""
The test main.py script using Pytest
"""
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, Response

from main import app


@pytest.fixture(scope="module")
def test_app() -> TestClient:
    """
    Fixture for the FastAPI TestClient.
    :return: FastAPI TestClient instance
    :rtype: TestClient
    """
    return TestClient(app)


@pytest.fixture(scope="module")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture for the HTTPX AsyncClient.
    :return: HTTPX AsyncClient instance
    :rtype: AsyncGenerator[AsyncClient, None]
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# pylint: disable=W0621
@pytest.mark.asyncio
async def test_welcome_message_async(async_client: AsyncClient) -> None:
    """
    Test for the welcome_message endpoint (async variant).
    :param async_client: AsyncClient instance
    :type async_client: AsyncClient
    :return: None
    :rtype: NoneType
    """
    response: Response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello, world!"}

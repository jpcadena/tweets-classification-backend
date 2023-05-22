"""
Test module for app/core/security/jwt.py
"""
from typing import Any, Dict, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, Response
from jose import jwt

from app.core.config import Settings
from app.core.security.jwt import create_access_token, create_refresh_token
from app.schemas.scope import Scope
from main import app


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, Any, None]:
    """
    Fixture for the TestClient.
    :return: TestClient instance
    :rtype: Generator[TestClient, Any, None]
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
async def async_client(client: TestClient) -> AsyncClient:
    """
    Fixture for the HTTPX AsyncClient.
    :param client: TestClient instance
    :type client: TestClient
    :return: HTTPX AsyncClient instance
    :rtype: AsyncClient
    """
    return AsyncClient(app=client.app, base_url="http://test")


def test_create_access_token(client: TestClient) -> None:
    """
    Test for create_access_token function.
    """
    payload = {"sub": "testuser", "scopes": [Scope.ACCESS_TOKEN.value]}
    token = create_access_token(payload)
    assert token is not None
    assert isinstance(token, str)


def test_create_refresh_token(client: TestClient) -> None:
    """
    Test for create_refresh_token function.
    """
    payload = {"sub": "testuser", "scopes": [Scope.REFRESH_TOKEN.value]}
    token = create_refresh_token(payload)
    assert token is not None
    assert isinstance(token, str)


@pytest.mark.asyncio
async def test_create_access_token_async(
        async_client: AsyncClient, app_settings: Settings
) -> None:
    """
    Test for create_access_token function (async variant).
    """
    payload = {"sub": "testuser", "scopes": [Scope.ACCESS_TOKEN.value]}
    response: Response = await async_client.post(
        f"{app_settings.API_V1_STR}/auth/token/access",
        json=payload)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    access_token = token_data["access_token"]
    decoded_token: Dict[str, Any] = jwt.decode(
        access_token, app_settings.SECRET_KEY,
        algorithms=[app_settings.ALGORITHM])
    assert decoded_token["sub"] == payload["sub"]
    assert decoded_token["scope"] == payload["scopes"]


@pytest.mark.asyncio
async def test_create_refresh_token_async(
        async_client: AsyncClient, app_settings: Settings
) -> None:
    """
    Test for create_refresh_token function (async variant).
    """
    payload = {"sub": "testuser", "scopes": [Scope.REFRESH_TOKEN.value]}
    response: Response = await async_client.post(
        f"{app_settings.API_V1_STR}/auth/token/refresh", json=payload)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    access_token = token_data["access_token"]
    decoded_token: Dict[str, Any] = jwt.decode(
        access_token, app_settings.SECRET_KEY,
        algorithms=[app_settings.ALGORITHM])
    assert decoded_token["sub"] == payload["sub"]
    assert decoded_token["scope"] == payload["scopes"]

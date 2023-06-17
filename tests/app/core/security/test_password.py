"""
Test module for app/core/security/password.py
"""
from typing import Any, Generator

import pytest
from fastapi.testclient import TestClient

from app.core.security.password import get_password_hash, verify_password
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


async def test_get_password_hash() -> None:
    """
    Test for get_password_hash function.
    """
    password: str = "password123"
    hashed_password = await get_password_hash(password)
    assert hashed_password is not None
    assert hashed_password != password


async def test_verify_password() -> None:
    """
    Test for verify_password function.
    """
    password: str = "password123"
    hashed_password = await get_password_hash(password)
    assert verify_password(hashed_password, password)
    assert not verify_password(hashed_password, "wrong_password")


@pytest.mark.parametrize(
    "hashed_password, plain_password",
    [
        ("$2b$12$uV5Hiz3C7p5vBb47wY/V9epgSZjZLnWvnqREg.4lcjR7EonZTO7sy",
         "password123"),
        ("$2b$12$uV5Hiz3C7p5vBb47wY/V9epgSZjZLnWvnqREg.4lcjR7EonZTO7sy",
         "wrong_password"),
        ("$2b$12$uV5Hiz3C7p5vBb47wY/V9epgSZjZLnWvnqREg.4lcjR7EonZTO7sy", ""),
        ("", "password123"),
        ("", ""),
    ]
)
def test_verify_password_with_params(
        hashed_password: str, plain_password: str
) -> None:
    """
    Parametrized test for verify_password function.
    """
    assert verify_password(hashed_password, plain_password)

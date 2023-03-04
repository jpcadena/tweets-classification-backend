"""

"""
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, status

from app.api.deps import get_current_user, RedisDependency


@pytest.fixture
def mock_user_service():
    user_service = MagicMock()
    user_service.get_login_user = AsyncMock(return_value=True)
    return user_service


@pytest.fixture
def mock_validate_token():
    return AsyncMock()


@pytest.mark.asyncio
async def test_get_current_user(mock_user_service, mock_validate_token):
    mock_user_service.get_login_user = AsyncMock(return_value=True)
    mock_validate_token.return_value = {"preferred_username": "test"}
    result = await get_current_user(token="123", settings={},
                                    user_service=mock_user_service,
                                    validate_token=mock_validate_token)
    assert result is not None


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_user_service,
                                              mock_validate_token):
    mock_user_service.get_login_user = AsyncMock(return_value=True)
    mock_validate_token.side_effect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED)
    with pytest.raises(HTTPException):
        await get_current_user(token="123", settings={},
                               user_service=mock_user_service,
                               validate_token=mock_validate_token)


@pytest.mark.asyncio
async def test_redis_dependency():
    redis_dependency: RedisDependency = RedisDependency()
    redis: RedisDependency = await redis_dependency()
    assert redis is not None

"""
This module handles JSON Web Token (JWT) creation for authentication
 and authorization.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Any

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from jose import jwt

from app.core import config
from app.core.decorators import with_logging, benchmark
from app.schemas.scope import Scope

logger: logging.Logger = logging.getLogger(__name__)


async def _generate_expiration_time(
        expires_delta: Optional[timedelta], minutes: Optional[float] = None
) -> datetime:
    """
    Generate an expiration time for JWT
    :param expires_delta: The timedelta specifying when the token
     should expire
    :type expires_delta: timedelta
    :param minutes: The minutes to add to the current time to get the
     expiration time
    :type minutes: float
    :return: The calculated expiration time
    :rtype: datetime
    """
    if expires_delta:
        return datetime.utcnow() + expires_delta
    if minutes is not None:
        return datetime.utcnow() + timedelta(minutes=minutes)
    raise ValueError("Either 'expires_delta' or 'minutes' must be provided.")


@with_logging
@benchmark
async def create_access_token(
        payload: dict[str, Any], scope: Scope = Scope.ACCESS_TOKEN,
        expires_delta: Optional[timedelta] = None,
        settings: config.Settings = Depends(config.get_settings),
) -> str:
    """
    Create a new JWT access token
    :param scope: The token's scope.
    :type scope: Scope
    :param payload: The payload or claims for the token
    :type payload: dict
    :param expires_delta: The timedelta specifying when the token should expire
    :type expires_delta: timedelta
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: The encoded JWT
    :rtype: str
    """
    expire_time: datetime = await _generate_expiration_time(
        expires_delta, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": int(expire_time.timestamp())})
    payload["scope"] = scope
    claims: dict[str, Any] = jsonable_encoder(payload)
    encoded_jwt: str = jwt.encode(
        claims=claims, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.info(
        "JWT created with JTI: %s for sub: %s. Expires in %s.",
        payload.get("jti"), payload.get("sub"),
        expire_time - datetime.utcnow())
    return encoded_jwt


@with_logging
async def create_refresh_token(
        payload: dict[str, Any],
        settings: config.Settings = Depends(config.get_settings)
) -> str:
    """
    Create a refresh token for authentication
    :param payload: The data to be used as payload in the token
    :type payload: dict[str, Any]
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    :return: The access token with refresh expiration time
    :rtype: str
    """
    expires: timedelta = timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    token: str = await create_access_token(
        payload=payload, scope=Scope.REFRESH_TOKEN, expires_delta=expires,
        settings=settings)
    return token

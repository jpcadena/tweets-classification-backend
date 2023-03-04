"""
JWT security script
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from jose import jwt
from passlib.context import CryptContext

from app.core import config
from app.core.decorators import with_logging, benchmark
from app.schemas.scope import Scope

logger: logging.Logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def _generate_expiration_time(
        expires_delta: Optional[timedelta],
        minutes: Optional[int] = None,
) -> datetime:
    """
    Generates expiration time
    :param expires_delta: The expiration delta
    :type expires_delta: timedelta
    :param minutes: The minutes to add
    :type minutes: int
    :return: The expiration time
    :rtype: datetime
    """
    if expires_delta:
        return datetime.utcnow() + expires_delta
    return datetime.utcnow() + timedelta(minutes=minutes)


@with_logging
@benchmark
async def create_access_token(
        payload: dict,
        scope: Scope = Scope.ACCESS_TOKEN,
        expires_delta: Optional[timedelta] = None,
        settings: config.Settings = Depends(config.get_settings),
) -> str:
    """
    Function to create a new access token
    :param scope: The token's scope.
    :type scope: Scope
    :param payload: claims for token
    :type payload: dict
    :param expires_delta: time expiration
    :type expires_delta: timedelta
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: encoded JWT
    :rtype: str
    """
    expire_time: datetime = await _generate_expiration_time(
        expires_delta, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({'exp': int(expire_time.timestamp())})
    payload['scope'] = scope
    claims: dict = jsonable_encoder(payload)
    encoded_jwt: str = jwt.encode(
        claims=claims, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    logger.info(
        "JWT created with JTI: %s for sub: %s. Expires in %s.",
        payload.get("jti"),
        payload.get("sub"),
        expire_time - datetime.utcnow(),
    )
    return encoded_jwt


@with_logging
async def create_refresh_token(
        payload: dict, settings: config.Settings = Depends(config.get_settings)
) -> str:
    """
    Create refresh token for authentication
    :param payload: data to be used as payload in Token
    :type payload: dict
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    :return: access token with refresh expiration time
    :rtype: str
    """
    expires: timedelta = timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    return await create_access_token(
        payload=payload, scope=Scope.REFRESH_TOKEN, expires_delta=expires,
        settings=settings)

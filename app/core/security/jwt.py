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

from app.core import config, logging_config
from app.core.decorators import with_logging, benchmark
from app.schemas.scope import Scope

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logging_config.setup_logging()
logger: logging.Logger = logging.getLogger(__name__)


@with_logging
@benchmark
async def create_access_token(
        payload: dict, scope: Scope = Scope.ACCESS_TOKEN,
        expires_delta: Optional[timedelta] = None,
        setting: config.Settings = Depends(config.get_setting)) -> str:
    """
    Function to create a new access token
    :param scope:
    :type scope:
    :param payload: claims for token
    :type payload: dict
    :param expires_delta: time expiration
    :type expires_delta: timedelta
    :param setting: Dependency method for cached setting object
    :type setting: config.Settings
    :return: encoded JWT
    :rtype: str
    """
    expire: datetime
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({'exp': int(expire.timestamp())})
    payload['scope'] = scope
    claims: dict = jsonable_encoder(payload)
    encoded_jwt: str = jwt.encode(claims=claims, key=setting.SECRET_KEY,
                                  algorithm=setting.ALGORITHM)
    logger.info(
        "JWT created with JTI: %s for sub: %s", payload.get('jti'),
        payload.get('sub'))
    return encoded_jwt


@with_logging
async def create_refresh_token(
        payload: dict, setting: config.Settings = Depends(config.get_setting)
) -> str:
    """
    Create refresh token for authentication
    :param payload: data to be used as payload in Token
    :type payload: dict
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    :return: access token with refresh expiration time
    :rtype: str
    """
    expires: timedelta = timedelta(
        minutes=setting.REFRESH_TOKEN_EXPIRE_MINUTES)
    return await create_access_token(
        payload=payload, scope=Scope.REFRESH_TOKEN, expires_delta=expires,
        setting=setting)

"""
API v1 Dependencies script
"""
from abc import ABC
from typing import Optional

from aioredis import Redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError

from app.core import config
from app.schemas.user import UserAuth
from app.services.user import UserService, get_user_service
from app.utils import audience

oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/login", scheme_name="JWT")


async def validate_token(token: str, setting: config.Settings) -> dict:
    """
    Validate the token.
    :param token: The token to validate
    :type token: str
    :param setting: Dependency method for cached setting object
    :type setting: config.Settings
    :return: The token decoded
    :rtype: dict
    """
    try:
        return jwt.decode(
            token=token,
            key=setting.SECRET_KEY,
            algorithms=[setting.ALGORITHM],
            options={"verify_subject": False},
            audience=audience,
            issuer=setting.SERVER_HOST
        )
    except jwt.ExpiredSignatureError as es_exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from es_exc
    except jwt.JWTClaimsError as jwtc_exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization claim is incorrect,"
                   " please check audience and issuer",
            headers={"WWW-Authenticate": "Bearer"},
        ) from jwtc_exc
    except (JWTError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        setting: config.Settings = Depends(config.get_setting),
        user_service: UserService = Depends(get_user_service)
) -> UserAuth:
    """
    Function to get current user
    :param token: access token from OAuth2PasswordBearer
    :type token: str
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    :param user_service: Dependency method for User service object
    :type user_service: UserService
    :return: current user from DB
    :rtype: UserAuth
    """
    try:
        payload = await validate_token(token, setting)
        username = payload.get("preferred_username")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = await user_service.get_login_user(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_auth = UserAuth(
            id=user.id, username=user.username, email=user.email)
        return user_auth
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


class RedisDependency:
    """
    FastAPI Dependency for Redis Connections
    """

    redis: Optional[ABC] = None

    async def __call__(self):
        if self.redis is None:
            await self.init()
        return self.redis

    async def init(self):
        """
        Initialises the Redis Dependency.
        :return: None
        :rtype: NoneType
        """
        setting: config.Settings = config.get_setting()
        url: str = setting.AIOREDIS_DATABASE_URI
        self.redis = await Redis.from_url(url, decode_responses=True)


redis_dependency: RedisDependency = RedisDependency()

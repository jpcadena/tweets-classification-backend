"""
API Dependencies script
"""
from abc import ABC
from typing import Optional, Annotated, Type

from aioredis import Redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, exceptions
from pydantic import ValidationError

from app.core import config
from app.core.config import Settings, get_settings
from app.schemas.user import UserAuth
from app.services.user import UserService, get_user_service

setting: Settings = get_settings()
oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl=setting.TOKEN_URL, scheme_name="JWT")
headers: dict[str, str] = {"WWW-Authenticate": "Bearer"}
detail: str = "Could not validate credentials"


async def validate_token(token: str, settings: Settings) -> dict:
    """
    Validate the token.
    :param token: The token to validate
    :type token: str
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: The token decoded
    :rtype: dict
    """
    try:
        return jwt.decode(
            token=token, key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM], options={"verify_subject": False},
            audience=settings.AUDIENCE, issuer=settings.SERVER_HOST)
    except exceptions.ExpiredSignatureError as es_exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired",
            headers=headers) from es_exc
    except exceptions.JWTClaimsError as c_exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization claim is incorrect,"
                   " please check audience and issuer", headers=headers
        ) from c_exc
    except (exceptions.JWTError, ValidationError) as exc:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail, headers) from exc


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        settings: config.Settings = Depends(config.get_settings),
        user_service: UserService = Depends(get_user_service)
) -> UserAuth:
    """
    Function to get current user
    :param token: access token from OAuth2PasswordBearer
    :type token: str
    :param settings: Dependency method for cached setting object
    :type settings: Settings
    :param user_service: Dependency method for User service object
    :type user_service: UserService
    :return: current user from DB
    :rtype: UserAuth
    """
    try:
        payload = await validate_token(token, settings)
        username = payload.get("preferred_username")
        if username is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail, headers)
        user = await user_service.get_login_user(username)
        if not user:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail, headers)
        user_auth = UserAuth(
            id=user.id, username=user.username, email=user.email)
        return user_auth
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail, headers) from exc


class RedisDependency:
    """
    FastAPI Dependency for Redis Connections
    """

    redis: Optional[ABC] = None

    async def __call__(self):
        if self.redis is None:
            await self.init()
        return self.redis

    async def init(self) -> None:
        """
        Initialises the Redis Dependency.
        :return: None
        :rtype: NoneType
        """
        url: str = str(setting.AIOREDIS_DATABASE_URI)
        self.redis = await Redis.from_url(url, decode_responses=True)


redis_dependency: RedisDependency = RedisDependency()
CurrentUser: Type[UserAuth] = Annotated[UserAuth, Depends(get_current_user)]

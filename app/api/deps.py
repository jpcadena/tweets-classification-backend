"""
API v1 Dependencies script
"""
from abc import ABC
from datetime import datetime
from typing import Optional
from aioredis import Redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import config
from app.db.session import database_session
from app.models import User
from app.schemas.token import TokenPayload
from app.schemas.user import UserAuth
from app.services.user import UserService
from app.utils import audience

oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/login", scheme_name="JWT")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        setting: config.Settings = Depends(config.get_setting),
        session: AsyncSession = Depends(database_session)
) -> UserAuth:
    """
    Function to get current user
    :param token: access token from OAuth2PasswordBearer
    :type token: str
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    :return: current user from DB
    :rtype: UserAuth
    """
    credentials_exception: HTTPException = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload: dict = jwt.decode(
            token=token, key=setting.SECRET_KEY,
            algorithms=[setting.ALGORITHM],
            options={"verify_subject": False}, audience=audience,
            issuer=setting.SERVER_HOST)
        token_data: TokenPayload = TokenPayload(**payload)
        username: str = payload.get("preferred_username")
        if username is None:
            raise credentials_exception
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.ExpiredSignatureError as es_exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token expired') from es_exc
    except jwt.JWTClaimsError as c_exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authorization claim is incorrect, please check'
                   ' audience and issuer') from c_exc
    except (JWTError, ValidationError) as exc:
        raise credentials_exception from exc
    user_service: UserService = UserService(session)
    user: User = await user_service.get_user_by_username(username)
    if not user:
        raise credentials_exception
    user_auth: UserAuth = UserAuth(
        id=user.id, username=user.username, email=user.email)
    return user_auth


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

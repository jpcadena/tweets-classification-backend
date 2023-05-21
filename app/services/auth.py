"""
Authentication Service
"""
import time
import uuid
from typing import Any

from fastapi import Depends

from app.core import config
from app.core.security.jwt import create_access_token, create_refresh_token
from app.models.user import User


class AuthService:
    """
    Service class for user authentication.
    """

    @staticmethod
    def _build_payload(user: User, settings: config.Settings) -> dict[str, Any]:
        """
        Build JWT payload for authentication
        :param user: User to authenticate
        :type user: User
        :param settings: Dependency method for cached setting object
        :type settings: config.Settings
        :return: Payload dictionary for JWT
        :rtype: dict[str, Any]
        """
        jti: uuid.UUID = uuid.uuid4()
        payload: dict[str, Any] = {
            "iss": settings.SERVER_HOST, "sub": "username:" + str(user.id),
            "aud": settings.AUDIENCE,
            "exp": int(time.time()) + int(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "nbf": int(time.time()) - 1, "iat": int(time.time()), "jti": jti,
            "nickname": user.username, "preferred_username": user.username,
            "email": user.email}
        return payload

    @staticmethod
    async def auth_token(
            user: User,
            settings: config.Settings = Depends(config.get_settings)
    ) -> tuple[str, str, str]:
        """
        Authenticate a user and generate access and refresh tokens
        :param user: User to authenticate
        :type user: User
        :param settings: Dependency method for cached setting object
        :type settings: config.Settings
        :return: Tuple containing the access token, refresh token, and
         token name
        :rtype: Tuple[str, str, str]
        """
        payload: dict[str, Any] = AuthService._build_payload(user, settings)
        access_token: str = await create_access_token(
            payload=payload, settings=settings)
        refresh_token: str = await create_refresh_token(
            payload=payload, settings=settings)
        name: str = str(user.id) + ":" + str(payload["jti"])
        return access_token, refresh_token, name

"""
Main script
"""
import time
import uuid

from fastapi import Depends

from app.core import config
from app.core.security.jwt import create_access_token, create_refresh_token
from app.models.user import User


class AuthService:
    """
    Authentication Service class.
    """

    @staticmethod
    async def auth_token(
            user: User,
            settings: config.Settings = Depends(config.get_settings)
    ) -> tuple[str, str, str]:
        """
        Authentication function for JWT
        :param user: User to authenticate
        :type user: User
        :param settings: Dependency method for cached setting object
        :type settings: config.Settings
        :return: Tuple with tokens and name for token
        :rtype: tuple[str, str, str]
        """
        jti: uuid.UUID = uuid.uuid4()
        payload: dict = {
            "iss": settings.SERVER_HOST, "sub": "username:" + str(user.id),
            "aud": settings.AUDIENCE,
            "exp": int(time.time()) + settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            "nbf": int(time.time()) - 1, "iat": int(time.time()),
            "jti": jti, "nickname": user.username,
            "preferred_username": user.username, "email": user.email}
        # if user.middle_name:
        #     payload["middle_name"] = user.middle_name
        #     first_names: str = user.first_name + ' ' + user.middle_name
        #     payload["name"] = first_names + ' ' + user.last_name
        # if user.gender:
        #     payload["gender"] = user.gender
        # if user.gender:
        #     payload["birthdate"] = user.birthdate
        # if user.gender:
        #     payload["phone_number"] = user.phone_number
        # if user.gender:
        #     payload["updated_at"] = user.updated_at
        access_token: str = await create_access_token(
            payload=payload,
            # scope=Scope.ACCESS_TOKEN, expires_delta=None,
            settings=settings)
        refresh_token: str = await create_refresh_token(
            payload=payload, settings=settings)
        name: str = str(user.id) + ':' + str(jti)
        return access_token, refresh_token, name

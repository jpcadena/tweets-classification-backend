"""
A module for jwt in the app.utils package.
"""
from typing import Optional

from fastapi import Depends
from jose import jwt

from app.core import config


async def encode_jwt(
        payload: dict,
        settings: config.Settings = Depends(config.get_settings)
) -> str:
    """
    Encode a JSON Web Token (JWT) with the given payload.
    :param payload: The payload to encode
    :type payload: dict
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: The JSON Web Token
    :rtype: str
    """
    encoded_jwt: str = jwt.encode(
        payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def decode_jwt(
        token: str,
        settings: config.Settings = Depends(config.get_settings)
) -> Optional[dict]:
    """
    Decode a JSON Web Token (JWT) and return the payload as a dictionary.
    :param token: The JSON Web Token
    :type token: str
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: The payload
    :rtype: dict
    """
    try:
        decoded_token: dict = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded_token
    except jwt.JWTError:
        return None

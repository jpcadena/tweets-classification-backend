"""
A module for jwt in the app.utils package.
"""
import logging
from typing import Any, Optional

from fastapi import Depends
from jose import exceptions, jwt

from app.core import config

logger: logging.Logger = logging.getLogger(__name__)


async def encode_jwt(
        payload: dict[str, Any],
        settings: config.Settings = Depends(config.get_settings)
) -> str:
    """
    Encode a JSON Web Token (JWT) with the given payload.
    :param payload: The payload to encode
    :type payload: dict[str, Any]
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: The JSON Web Token
    :rtype: str
    """
    return jwt.encode(
        payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def decode_jwt(
        token: str,
        settings: config.Settings = Depends(config.get_settings)
) -> Optional[dict[str, Any]]:
    """
    Decode a JSON Web Token (JWT) and return the payload as a dictionary.
    :param token: The JSON Web Token
    :type token: str
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: The payload
    :rtype: Optional[dict[str, Any]]
    """
    try:
        decoded_token: dict[str, Any] = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded_token
    except exceptions.JWTError as exc:
        logger.error(exc)
        return None

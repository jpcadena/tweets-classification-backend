"""
A module for password in the app.utils package.
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import Depends
from pydantic import EmailStr

from app.core import config
from app.utils.security.jwt import decode_jwt, encode_jwt

logger: logging.Logger = logging.getLogger(__name__)


async def generate_password_reset_payload(
        email: EmailStr, settings: config.Settings
) -> dict[str, Any]:
    """
    Generate a password reset payload
    :param email: The email to generate the reset token for
    :type email: EmailStr
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: The payload to be used
    :rtype: dict[str, Any]
    """
    now: datetime = datetime.utcnow()
    expires: datetime = now + timedelta(
        hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    exp: float = expires.timestamp()
    payload: dict[str, Any] = {"exp": exp, "nbf": now, "sub": email}
    logger.info("Payload generated for password")
    return payload


async def generate_password_reset_token(
        email: EmailStr,
        settings: config.Settings = Depends(config.get_settings)
) -> str:
    """
    Generate a password reset token for the given email address.
    :param email: The email to generate the reset token for
    :type email: EmailStr
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: The password reset token
    :rtype: str
    """
    payload: dict[str, Any] = await generate_password_reset_payload(
        email, settings)
    return await encode_jwt(payload, settings)


async def verify_password_reset_token(
        token: str,
        settings: config.Settings = Depends(config.get_settings)
) -> Optional[EmailStr]:
    """
    Verify a password reset token and return the email address if valid.
    :param token: The JSON Web Token
    :type token: str
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: The email address
    :rtype: EmailStr
    """
    decoded_token: dict[str, Any] = await decode_jwt(token, settings)
    if decoded_token:
        return decoded_token.get("sub")
    return None

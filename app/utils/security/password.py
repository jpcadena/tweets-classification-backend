"""
A module for password in the app.utils package.
"""
from datetime import timedelta, datetime
from typing import Optional

from fastapi import Depends
from pydantic import EmailStr

from app.core import config
from app.utils.security.jwt import encode_jwt, decode_jwt


async def generate_password_reset_payload(
        email: EmailStr, settings: config.Settings
) -> dict:
    """
    Generate a password reset payload
    :param email: The email to generate the reset token for
    :type email: EmailStr
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: The payload to be used
    :rtype: dict
    """
    delta: timedelta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now: datetime = datetime.utcnow()
    expires: datetime = now + delta
    exp: float = expires.timestamp()
    payload: dict = {"exp": exp, "nbf": now, "sub": email}
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
    payload: dict = await generate_password_reset_payload(email, settings)
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
    decoded_token: dict = await decode_jwt(token, settings)
    if decoded_token:
        return decoded_token.get("sub")
    return None

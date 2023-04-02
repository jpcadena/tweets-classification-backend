"""
App utils script
"""
import logging
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import Depends
from jose import jwt
from pydantic import EmailStr, AnyHttpUrl

from app.core import config
from app.core.decorators import with_logging, benchmark
from app.utils.email_notifications import read_template_file, send_email
from app.utils.metadata import read_json_file, write_json_file, \
    modify_json_data

logger: logging.Logger = logging.getLogger(__name__)

telephone_regex: str = r"\(?\+[0-9]{1,3}\)? ?-?[0-9]{1,3} ?-?[0-9]{3,5}?-?" \
                       r"[0-9]{4}( ?-?[0-9]{3})? ?(\w{1,10}\s?\d{1,6})?"
password_regex: str = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?" \
                      r"[#?!@$%^&*-]).{8,14}$"
sub_regex: str = r"username:(?!0)\d+"


async def send_test_email(
        email_to: EmailStr,
        settings: config.Settings = Depends(config.get_settings)) -> bool:
    """
    Send test email
    :param email_to: The email address of the recipient
    :type email_to: EmailStr
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: True if the email was sent; otherwise false
    :rtype: bool
    """
    subject: str = f"{settings.PROJECT_NAME} - Test email"
    template_path = Path(settings.EMAIL_TEMPLATES_DIR) / "test_email.html"
    template_str: str = await read_template_file(template_path, settings)
    is_sent: bool = await send_email(
        email_to=email_to, subject_template=subject,
        html_template=template_str,
        environment={"project_name": settings.PROJECT_NAME, "email": email_to},
        settings=settings)
    return is_sent


async def send_reset_password_email(
        email_to: EmailStr, username: str, token: str,
        settings: config.Settings = Depends(config.get_settings)) -> bool:
    """
    Sends a password reset email to a user with the given email address
    :param email_to: The email address of the user
    :type email_to: EmailStr
    :param username: The username of the user
    :type username: str
    :param token: The reset password token generated for the user
    :type token: str
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: True if the email was sent successfully; False otherwise
    :rtype: bool
    """
    subject: str = f"{settings.PROJECT_NAME} - Password recovery for user " \
                   f"{username}"
    template_path = Path(settings.EMAIL_TEMPLATES_DIR) / "reset_password.html"
    template_str: str = await read_template_file(template_path, settings)
    server_host: AnyHttpUrl = settings.SERVER_HOST
    link: str = f"{server_host}/reset-password?token={token}"
    is_sent: bool = await send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME, "username": username,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link}, settings=settings)
    return is_sent


async def send_new_account_email(
        email_to: EmailStr, username: str,
        settings: config.Settings = Depends(config.get_settings)) -> bool:
    """
    Send a new account email
    :param email_to: The email address of the recipient with new
     account
    :type email_to: EmailStr
    :param username: Username of the recipient
    :type username: str
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: True if the email was sent; otherwise false
    :rtype: bool
    """
    subject: str = f"{settings.PROJECT_NAME} - New account for user {username}"
    template_path = Path(settings.EMAIL_TEMPLATES_DIR) / "new_account.html"
    template_str: str = await read_template_file(template_path, settings)
    link = settings.SERVER_HOST
    is_sent: bool = await send_email(
        email_to=email_to, subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME, "username": username,
            "email": email_to, "link": link}, settings=settings)
    return is_sent


async def encode_jwt(
        payload: dict,
        settings: config.Settings = Depends(config.get_settings)) -> str:
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


async def generate_password_reset_token(
        email: EmailStr,
        settings: config.Settings = Depends(config.get_settings)) -> str:
    """
    Generate a password reset token for the given email address.
    :param email: The email to generate the reset token for
    :type email: EmailStr
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: The password reset token
    :rtype: str
    """
    delta: timedelta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now: datetime = datetime.utcnow()
    expires: datetime = now + delta
    exp: float = expires.timestamp()
    payload: dict = {"exp": exp, "nbf": now, "sub": email}
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


async def hide_email(email: EmailStr) -> str:
    """
    Hide email using **** for some characters
    :param email: Email address to hide some values
    :type email: EmailStr
    :return: Email address with some **** for its value
    :rtype: str
    """
    email_title, email_domain = email.split("@")
    title_count: int = max(math.ceil(len(email_title) / 2), 1)
    domain_sections = email_domain.split(".")
    domain_first_section = domain_sections[0]
    domain_count: int = max(math.ceil(len(domain_first_section) / 2), 1)
    replaced_title: str = email_title.replace(
        email_title[title_count * -1:], "*" * title_count)
    replaced_domain_first: str = domain_first_section.replace(
        domain_first_section[domain_count * -1:], "*" * domain_count)
    replaced_domain: str = replaced_domain_first + "." + ".".join(
        domain_sections[1:])
    hidden_email: str = f"{replaced_title}@{replaced_domain}"
    return hidden_email


@with_logging
@benchmark
async def update_json(
        settings: config.Settings = Depends(config.get_settings)) -> None:
    """
    Update JSON file for client
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: None
    :rtype: NoneType
    """
    data: dict = await read_json_file(settings)
    data: dict = await modify_json_data(data)
    await write_json_file(data, settings)
    logger.info("Updated OpenAPI JSON file")

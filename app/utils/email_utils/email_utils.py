"""
A module for email utilities in the app.utils package.
"""
from pathlib import Path

from fastapi import Depends
from pydantic import EmailStr

from app.core import config
from app.core.decorators import with_logging
from app.utils.email_utils.notificaction import send_email
from app.utils.email_utils.template import read_template_file


async def build_email_template(
        template_file: str, settings: config.Settings
) -> str:
    """
    Builds the email template
    :param template_file: The template file
    :type template_file: str
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: The template read as a string
    :rtype: str
    """
    template_path: Path = Path(settings.EMAIL_TEMPLATES_DIR) / template_file
    template_str: str = await read_template_file(template_path, settings)
    return template_str


@with_logging
async def send_test_email(
        email_to: EmailStr,
        settings: config.Settings = Depends(config.get_settings)
) -> bool:
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
    template_str: str = await build_email_template("test_email.html", settings)
    is_sent: bool = await send_email(
        email_to=email_to, subject_template=subject,
        html_template=template_str,
        environment={"project_name": settings.PROJECT_NAME, "email": email_to},
        settings=settings)
    return is_sent


@with_logging
async def send_reset_password_email(
        email_to: EmailStr, username: str, token: str,
        settings: config.Settings = Depends(config.get_settings)
) -> bool:
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
    template_str: str = await build_email_template(
        "reset_password.html", settings)
    link: str = f"{settings.SERVER_HOST}/reset-password?token={token}"
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


@with_logging
async def send_new_account_email(
        email_to: EmailStr, username: str,
        settings: config.Settings = Depends(config.get_settings)
) -> bool:
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
    template_str: str = await build_email_template("new_account.html", settings)
    is_sent: bool = await send_email(
        email_to=email_to, subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME, "username": username,
            "email": email_to, "link": settings.SERVER_HOST}, settings=settings)
    return is_sent

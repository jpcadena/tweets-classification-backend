"""
Email notifications script
"""
import logging
import smtplib
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Union

import aiofiles
from fastapi import Depends
from jinja2 import Template
from pydantic import EmailStr

from app.core import config
from app.core.decorators import with_logging, benchmark

logger: logging.Logger = logging.getLogger(__name__)


async def render_template(template: str, environment: dict[str, Any]) -> str:
    """
    Renders the given template with the given environment variables
    :param template: The body of the email in HTML format
    :type template: str
    :param environment: A dictionary of variables used in the email
     templates
    :type environment: dict[str, Any]
    :return: Rendered template with environment variables
    :rtype: str
    """
    return Template(template).render(environment)


async def create_message(
        html: str, subject: str,
        settings: config.Settings = Depends(config.get_settings)) -> MIMEText:
    """
    Creates an email message with the given HTML content and subject
    :param html: Rendered template with environment variables
    :type html: str
    :param subject: The subject of the email
    :type subject: str
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: Message with subject and rendered template
    :rtype: MIMEText
    """
    message: MIMEText = MIMEText(html, "html")
    message["Subject"] = subject
    message[
        "From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    logger.info("Message created from: %s", settings.EMAILS_FROM_EMAIL)
    return message


async def login_to_smtp(
        smtp_conn: smtplib.SMTP, setting: config.Settings
) -> bool:
    """
    Logs in the SMTP server with the given credentials.
    :param smtp_conn: SMTP connection object
    :type smtp_conn: SMTP
    :param setting: Dependency method for cached setting object
    :type setting: config.Settings
    :return: True if the login was successful, otherwise False
    :rtype: bool
    """
    try:
        if setting.SMTP_USER and setting.SMTP_PASSWORD:
            smtp_conn.login(setting.SMTP_USER, setting.SMTP_PASSWORD)
        return True
    except smtplib.SMTPException as exc:
        logger.error("SMTP login error.\n%s", exc)
        return False


@with_logging
@benchmark
async def send_message(
        email_to: EmailStr, message: MIMEText,
        settings: config.Settings = Depends(config.get_settings)
) -> Union[bool, str]:
    """
    Sends the message to the given email address.
    :param email_to: The email address of the recipient
    :type email_to: EmailStr
    :param message: Message with subject and rendered template
    :type message: MIMEText
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: True if the email was sent; otherwise an error message
    :rtype: Union[bool, str]
    """
    smtp_options: dict = {"host": settings.SMTP_HOST,
                          "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["starttls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    try:
        with smtplib.SMTP(
                smtp_options["host"], smtp_options["port"],
                timeout=settings.MAIL_TIMEOUT) as smtp_conn:
            if smtp_options.get("starttls"):
                smtp_conn.starttls()
            await login_to_smtp(smtp_conn, settings)
            smtp_conn.sendmail(
                settings.EMAILS_FROM_EMAIL, [email_to], message.as_string())
        logger.info("sent email to %s", email_to)
        return True
    except smtplib.SMTPException as exc:
        error_msg = f"error sending email to {email_to}.\n{exc}"
        logger.error(error_msg)
        return error_msg


async def send_email(
        email_to: EmailStr, subject_template: str = "",
        html_template: str = "", environment: dict[str, Any] = None,
        settings: config.Settings = Depends(config.get_settings)) -> bool:
    """
    Send an e-mail to a recipient.
    :param settings:
    :type settings:
    :param email_to: The email address of the recipient
    :type email_to: EmailStr
    :param subject_template: The subject of the email
    :type subject_template: str
    :param html_template: The body of the email in HTML format
    :type html_template: str
    :param environment: A dictionary of variables used in the email
     templates
    :type environment: dict[str, Any]
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: True if the email was sent; otherwise false
    :rtype: bool
    """
    assert settings.EMAILS_ENABLED, \
        "no provided configuration for email variables"
    subject: str = await render_template(subject_template, environment)
    html: str = await render_template(html_template, environment)
    message: MIMEText = await create_message(html, subject, settings)
    is_sent: bool = await send_message(email_to, message, settings)
    return is_sent


async def read_template_file(
        template_path: Union[str, Path],
        settings: config.Settings = Depends(config.get_settings)) -> str:
    """
    Read the template file
    :param template_path: Path to the template
    :type template_path: str
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: Template string
    :rtype: str
    """
    async with aiofiles.open(template_path, mode="r",
                             encoding=settings.ENCODING) as file:
        return await file.read()

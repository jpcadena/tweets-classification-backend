"""
A module for message in the app.utils package.
"""
import logging
import smtplib
from email.mime.text import MIMEText
from typing import Any, Union

from fastapi import Depends
from pydantic import EmailStr

from app.core import config
from app.core.decorators import benchmark, with_logging

logger: logging.Logger = logging.getLogger(__name__)


async def create_message(
        html: str, subject: str,
        settings: config.Settings = Depends(config.get_settings)
) -> MIMEText:
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
    smtp_options: dict[str, Any] = {
        "host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
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
                str(settings.EMAILS_FROM_EMAIL), [email_to],
                message.as_string())
        logger.info("sent email to %s", email_to)
        return True
    except smtplib.SMTPException as exc:
        error_msg = f"error sending email to {email_to}.\n{exc}"
        logger.error(error_msg)
        return error_msg

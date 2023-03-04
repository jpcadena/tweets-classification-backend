"""
Email notifications script
"""
import logging
import smtplib
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Union

import aiofiles
from jinja2 import Template
from pydantic import EmailStr

from app.core.config import settings
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


async def create_message(html: str, subject: str) -> MIMEText:
    """
    Creates an email message with the given HTML content and subject
    :param html: Rendered template with environment variables
    :type html: str
    :param subject: The subject of the email
    :type subject: str
    :return: Message with subject and rendered template
    :rtype: MIMEText
    """
    message: MIMEText = MIMEText(html, "html")
    message["Subject"] = subject
    message[
        "From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    logger.info("Message created from: %s", settings.EMAILS_FROM_EMAIL)
    return message


@with_logging
@benchmark
async def send_message(email_to: EmailStr, message: MIMEText) -> bool:
    """
    Sends the message to the given email address.
    :param email_to: The email address of the recipient
    :type email_to: EmailStr
    :param message: Message with subject and rendered template
    :type message: MIMEText
    :return: True if the email was sent; otherwise false
    :rtype: bool
    """
    smtp_options: dict = {"host": settings.SMTP_HOST,
                          "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["starttls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    is_sent: bool = False
    try:
        smtp_conn: smtplib.SMTP = smtplib.SMTP(
            settings.SMTP_HOST, settings.SMTP_PORT)
        if settings.SMTP_TLS:
            smtp_conn.starttls()
        if settings.SMTP_USER:
            smtp_conn.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp_conn.sendmail(
            settings.EMAILS_FROM_EMAIL, [email_to], message.as_string())
        smtp_conn.quit()
        is_sent = True
        logger.info("sent email to %s", email_to)
    except smtplib.SMTPException as exc:
        logger.error("error sending email to %s.\n%s", email_to, exc)
    return is_sent


async def send_email(
        email_to: EmailStr, subject_template: str = "",
        html_template: str = "", environment: dict[str, Any] = None) -> bool:
    """
    Send an e-mail to a recipient.
    :param email_to: The email address of the recipient
    :type email_to: EmailStr
    :param subject_template: The subject of the email
    :type subject_template: str
    :param html_template: The body of the email in HTML format
    :type html_template: str
    :param environment: A dictionary of variables used in the email
     templates
    :type environment: dict[str, Any]
    :return: True if the email was sent; otherwise false
    :rtype: bool
    """
    assert settings.EMAILS_ENABLED, \
        "no provided configuration for email variables"
    subject: str = await render_template(subject_template, environment)
    html: str = await render_template(html_template, environment)
    message: MIMEText = await create_message(html, subject)
    is_sent: bool = await send_message(email_to, message)
    return is_sent


async def read_template_file(template_path: Union[str, Path]) -> str:
    """
    Read the template file
    :param template_path: Path to the template
    :type template_path: str
    :return: Template string
    :rtype: str
    """
    async with aiofiles.open(template_path, mode="r",
                             encoding=settings.ENCODING) as file:
        return await file.read()

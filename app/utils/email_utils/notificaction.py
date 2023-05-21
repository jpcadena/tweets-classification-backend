"""
A module for email notifications in the app.utils package.
"""
import logging
from email.mime.text import MIMEText
from typing import Any

from fastapi import Depends
from pydantic import EmailStr

from app.core import config
from app.utils.email_utils.message import create_message, send_message
from app.utils.email_utils.template import render_template

logger: logging.Logger = logging.getLogger(__name__)


async def send_email(
        email_to: EmailStr, subject_template: str,
        html_template: str, environment: dict[str, Any],
        settings: config.Settings = Depends(config.get_settings)
) -> bool:
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

"""
App utils script
"""
import json
import logging
import math
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Optional, Union

import aiofiles
from jinja2 import Template
from jose import jwt
from pydantic import EmailStr, AnyHttpUrl

from app.core import logging_config
from app.core.config import settings
from app.core.decorators import with_logging, benchmark

logging_config.setup_logging()
logger: logging.Logger = logging.getLogger(__name__)

telephone_regex: str = r"\(?\+[0-9]{1,3}\)? ?-?[0-9]{1,3} ?-?[0-9]{3,5}?-?" \
                       r"[0-9]{4}( ?-?[0-9]{3})? ?(\w{1,10}\s?\d{1,6})?"
password_regex: str = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?" \
                      r"[#?!@$%^&*-]).{8,14}$"
sub_regex: str = r'username:(?!0)\d+'
audience: str = f'{settings.SERVER_HOST}{settings.API_V1_STR}/auth/login'


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
    print("Message created from: %s", settings.EMAILS_FROM_EMAIL)
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
        print("sent email to %s", email_to)
    except smtplib.SMTPException as exc:
        print("error sending email to %s.\n%s", email_to, exc)
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
    is_sent: bool = send_message(email_to, message)
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


async def send_test_email(email_to: EmailStr) -> bool:
    """
    Send test email
    :param email_to: The email address of the recipient
    :type email_to: EmailStr
    :return: True if the email was sent; otherwise false
    :rtype: bool
    """
    subject: str = f"{settings.PROJECT_NAME} - Test email"
    template_path = Path(settings.EMAIL_TEMPLATES_DIR) / "test_email.html"
    template_str: str = await read_template_file(template_path)
    is_sent: bool = await send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": settings.PROJECT_NAME, "email": email_to})
    return is_sent


async def send_reset_password_email(
        email_to: EmailStr, username: str, token: str) -> bool:
    """
    Sends a password reset email to a user with the given email address
    :param email_to: The email address of the user
    :type email_to: EmailStr
    :param username: The username of the user
    :type username: str
    :param token: The reset password token generated for the user
    :type token: str
    :return: True if the email was sent successfully; False otherwise
    :rtype: bool
    """
    subject: str = f"{settings.PROJECT_NAME} - Password recovery for user " \
                   f"{username}"
    template_path = Path(settings.EMAIL_TEMPLATES_DIR) / "reset_password.html"
    template_str: str = await read_template_file(template_path)
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
            "link": link})
    return is_sent


async def send_new_account_email(
        email_to: EmailStr, username: str) -> bool:
    """
    Send a new account email
    :param email_to: The email address of the recipient with new
     account
    :type email_to: EmailStr
    :param username: Username of the recipient
    :type username: str
    :return: True if the email was sent; otherwise false
    :rtype: bool
    """
    subject: str = f"{settings.PROJECT_NAME} - New account for user {username}"
    template_path = Path(settings.EMAIL_TEMPLATES_DIR) / "new_account.html"
    template_str: str = await read_template_file(template_path)
    link = settings.SERVER_HOST
    is_sent: bool = await send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME, "username": username,
            "email": email_to, "link": link})
    return is_sent


def generate_password_reset_token(email: EmailStr) -> str:
    """

    :param email: The email address of the recipient
    :type email: EmailStr
    :return:
    :rtype: str
    """
    delta: timedelta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now: datetime = datetime.utcnow()
    expires: datetime = now + delta
    exp: float = expires.timestamp()
    encoded_jwt: str = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email}, settings.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify password reset token
    :param token:
    :type token: str
    :return:
    :rtype: str or NoneType
    """
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY,
                                   algorithms=["HS256"])
        return decoded_token["email"]
    except jwt.JWTError:
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
        email_title[title_count * -1:], '*' * title_count)
    replaced_domain_first: str = domain_first_section.replace(
        domain_first_section[domain_count * -1:], '*' * domain_count)
    replaced_domain: str = replaced_domain_first + '.' + '.'.join(
        domain_sections[1:])
    hidden_email: str = f'{replaced_title}@{replaced_domain}'
    return hidden_email


@with_logging
@benchmark
async def update_json() -> None:
    """
    Update JSON file for client
    :return: None
    :rtype: NoneType
    """
    file_path: str = '.' + settings.OPENAPI_FILE_PATH
    async with aiofiles.open(
            file_path, mode='r', encoding=settings.ENCODING) as file:
        content: str = await file.read()
    data: dict = json.loads(content)
    for key, path_data in data["paths"].items():
        if key == '/':
            continue
        for operation in path_data.values():
            tag: str = operation["tags"][0]
            operation_id: str = operation["operationId"]
            to_remove: str = f"{tag}-"
            # new_operation_id = operation_id[len(to_remove):]
            new_operation_id = operation_id.removeprefix(to_remove)
            operation["operationId"] = new_operation_id
    # print(json.dumps(data, indent=4))
    async with aiofiles.open(
            file_path, mode='w', encoding=settings.ENCODING) as out_file:
        await out_file.write(json.dumps(data, indent=4))
    logger.info("Updated OpenAPI JSON file")

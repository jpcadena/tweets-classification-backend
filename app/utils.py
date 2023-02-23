"""
App utils script
"""
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import logging
import math
import smtplib
from pathlib import Path
from typing import Any, Optional
from jinja2 import Template
from jose import jwt
from pydantic import EmailStr
from app.core.config import settings

telephone_regex: str = r"\(?\+[0-9]{1,3}\)? ?-?[0-9]{1,3} ?-?[0-9]{3,5}?-?" \
                       r"[0-9]{4}( ?-?[0-9]{3})? ?(\w{1,10}\s?\d{1,6})?"
password_regex: str = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?" \
                      r"[#?!@$%^&*-]).{8,14}$"
sub_regex: str = r'username:(?!0)\d+'
audience: str = f'{settings.SERVER_HOST}{settings.API_V1_STR}/auth/login'


def send_email(
        email_to: str, subject_template: str = "", html_template: str = "",
        environment: dict[str, Any] = None) -> None:
    assert settings.EMAILS_ENABLED, "no provided configuration for email " \
                                    "variables"
    subject = Template(subject_template).render(environment)
    html = Template(html_template).render(environment)
    message = MIMEText(html, "html")
    message["Subject"] = subject
    message[
        "From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    message["To"] = email_to
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["starttls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    smtp_conn = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
    if settings.SMTP_TLS:
        smtp_conn.starttls()
    if settings.SMTP_USER:
        smtp_conn.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
    smtp_conn.sendmail(settings.EMAILS_FROM_EMAIL, [email_to],
                       message.as_string())
    smtp_conn.quit()
    logging.info("sent email to %s with subject '%s'", email_to, subject)


def send_test_email(email_to: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "test_email.html",
              encoding=settings.ENCODING) as file:
        template_str = file.read()
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": settings.PROJECT_NAME, "email": email_to},
    )


def send_reset_password_email(email_to: str, email: str, token: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "reset_password.html",
              encoding=settings.ENCODING) as file:
        template_str = file.read()
    server_host = settings.SERVER_HOST
    link = f"{server_host}/reset-password?token={token}"
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )


def send_new_account_email(email_to: str, username: str,
                           password: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "new_account.html",
              encoding=settings.ENCODING) as file:
        template_str = file.read()
    link = settings.SERVER_HOST
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": link,
        },
    )


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email}, settings.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY,
                                   algorithms=["HS256"])
        return decoded_token["email"]
    except jwt.JWTError:
        return None


async def hide_email(email: EmailStr) -> str:
    email_split: list[str] = email.split("@")
    email_title: str = email_split[0]
    email_domain: str = email_split[1]
    line_count: int = max(math.ceil(len(email_title) / 2), 1)
    replaced_title: str = email_title.replace(
        email_title[line_count * -1:], '*' * line_count)
    hidden_email: str = f'{replaced_title}@{email_domain}'
    return hidden_email

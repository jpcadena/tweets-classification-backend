"""
A module for general utilities in the app.utils package.
"""
import logging
import math
from typing import Any

from fastapi import Depends
from pydantic import EmailStr

from app.core import config
from app.core.decorators import with_logging, benchmark
from app.utils.files_utils.json_utils import read_json_file, write_json_file
from app.utils.files_utils.openapi_utils import modify_json_data

logger: logging.Logger = logging.getLogger(__name__)


@with_logging
@benchmark
async def update_json(
        settings: config.Settings = Depends(config.get_settings)
) -> None:
    """
    Update JSON file for client
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: None
    :rtype: NoneType
    """
    data: dict[str, Any] = await read_json_file(settings)
    data = await modify_json_data(data)
    await write_json_file(data, settings)
    logger.info("Updated OpenAPI JSON file")


@with_logging
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

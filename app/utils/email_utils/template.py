"""
A module for template in the app.utils package.
"""
import logging
from pathlib import Path
from typing import Any, Union

import aiofiles
from fastapi import Depends
from jinja2 import Template

from app.core import config
from app.core.decorators import benchmark, with_logging

logger: logging.Logger = logging.getLogger(__name__)


@with_logging
@benchmark
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


@with_logging
@benchmark
async def read_template_file(
        template_path: Union[str, Path],
        settings: config.Settings = Depends(config.get_settings)
) -> str:
    """
    Read the template file
    :param template_path: Path to the template
    :type template_path: Union[str, Path]
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: Template string
    :rtype: str
    """
    async with aiofiles.open(
            template_path, mode="r", encoding=settings.ENCODING) as file:
        return await file.read()

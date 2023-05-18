"""
A module for json utils in the app.utils package.
"""
import json
from typing import Any

import aiofiles
from fastapi import Depends

from app.core import config


async def read_json_file(
        settings: config.Settings = Depends(config.get_settings)
) -> dict[str, Any]:
    """
    Read the OpenAPI JSON file
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: JSON data
    :rtype: dict[str, Any]
    """
    file_path: str = f".{settings.OPENAPI_FILE_PATH}"
    async with aiofiles.open(
            file_path, mode="r", encoding=settings.ENCODING) as file:
        content: str = await file.read()
    data: dict[str, Any] = json.loads(content)
    return data


async def write_json_file(
        data: dict[str, Any],
        settings: config.Settings = Depends(config.get_settings)
) -> None:
    """
    Write the modified JSON data back to the file
    :param data: Modified JSON data
    :type data: dict[str, Any]
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: None
    :rtype: NoneType
    """
    file_path: str = f".{settings.OPENAPI_FILE_PATH}"
    async with aiofiles.open(
            file_path, mode="w", encoding=settings.ENCODING) as out_file:
        await out_file.write(json.dumps(data, indent=4))

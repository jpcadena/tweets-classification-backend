"""
Metadata script
"""
import json

import aiofiles
from fastapi import Depends

from app.core import config


async def read_json_file(
        settings: config.Settings = Depends(config.get_settings)) -> dict:
    """
    Read the OpenAPI JSON file
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: JSON data
    :rtype: dict
    """
    file_path: str = "." + settings.OPENAPI_FILE_PATH
    async with aiofiles.open(
            file_path, mode="r", encoding=settings.ENCODING) as file:
        content: str = await file.read()
    data: dict = json.loads(content)
    return data


async def remove_tag_from_operation_id(tag: str, operation_id: str) -> str:
    """
    Remove tag from the operation ID
    :param tag: Tag to remove
    :type tag: str
    :param operation_id: Original operation ID
    :type operation_id: str
    :return: Updated operation ID
    :rtype: str
    """
    to_remove: str = f"{tag}-"
    new_operation_id: str = operation_id.removeprefix(to_remove)
    return new_operation_id


async def update_operation_id(operation: dict) -> None:
    """
    Update the operation ID of a single operation.
    :param operation: Operation object
    :type operation: dict
    :return: None
    :rtype: NoneType
    """
    tag: str = operation["tags"][0]
    operation_id: str = operation["operationId"]
    new_operation_id: str = await remove_tag_from_operation_id(
        tag, operation_id)
    operation["operationId"] = new_operation_id


async def modify_json_data(data: dict) -> dict:
    """
    Modify the JSON data
    :param data: JSON data to modify
    :type data: dict
    :return: Modified JSON data
    :rtype: dict
    """
    for key, path_data in data["paths"].items():
        if key == "/":
            continue
        for _, operation in dict(path_data).items():
            await update_operation_id(operation)
    return data


async def write_json_file(
        data: dict, settings: config.Settings = Depends(config.get_settings)
) -> None:
    """
    Write the modified JSON data back to the file
    :param data: Modified JSON data
    :type data: dict
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: None
    :rtype: NoneType
    """
    file_path: str = "." + settings.OPENAPI_FILE_PATH
    async with aiofiles.open(
            file_path, mode="w", encoding=settings.ENCODING) as out_file:
        await out_file.write(json.dumps(data, indent=4))

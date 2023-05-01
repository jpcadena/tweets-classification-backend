"""
Metadata script
"""


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
    return operation_id.removeprefix(f"{tag}-")


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

"""
This script provides functions for interacting with the authentication
 (Redis) database.
"""
import logging
from typing import Any, Callable

import aioredis
from aioredis.exceptions import AuthenticationError
from aioredis.exceptions import ConnectionError as RedisConnectionError
from aioredis.exceptions import DataError, NoPermissionError
from aioredis.exceptions import TimeoutError as RedisTimeoutError
from fastapi import Depends

from app.core import config
from app.core.decorators import benchmark, with_logging

logger: logging.Logger = logging.getLogger(__name__)


@with_logging
@benchmark
async def init_auth_db(
        settings: config.Settings = Depends(config.get_settings)
) -> None:
    """
    Initialize connection to the Redis database for authentication
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: None
    :rtype: NoneType
    """
    await aioredis.from_url(
        settings.AIOREDIS_DATABASE_URI, decode_responses=True)
    logger.info("Redis Database initialized")


def handle_redis_exceptions(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator for handling Redis exceptions
    :param func: The function to be decorated
    :type func: Callable[..., Any]
    :return: The decorated function.
    :rtype: Callable[..., Any]
    """

    async def inner(*args: Any, **kwargs: Any) -> Any:
        """
        Inner function to handle Redis exceptions.
        :param args: The arguments to be decorated.
        :type args: Any
        :param kwargs: The keyword arguments to be decorated.
        :type kwargs: Any
        :return: The return value of the function or None if an
         exception occurs.
        :rtype: Any
        """
        try:
            return await func(*args, **kwargs)
        except (AuthenticationError, RedisConnectionError, DataError,
                NoPermissionError, RedisTimeoutError) as exc:
            logger.error(exc)
            return None

    return inner

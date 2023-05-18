"""
Authentication database script
"""
import logging
from typing import Callable, Any

import aioredis
from aioredis.exceptions import DataError, AuthenticationError, \
    NoPermissionError, TimeoutError as RedisTimeoutError, \
    ConnectionError as RedisConnectionError
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
    Init connection to Redis Database
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
    Decorator for Redis Exceptions
    :param func: function to be decorated
    :return: return from func or exception raised
    """

    async def inner(*args: Any, **kwargs: Any) -> Any:
        """
        Inner function to handle
        :param args: Arguments to be decorated
        :type args: Any
        :param kwargs: Keyword arguments to be decorated
        :type kwargs: Any
        :return: Callable function return
        :rtype: Callable
        """
        try:
            return await func(*args, **kwargs)
        except (AuthenticationError, RedisConnectionError, DataError,
                NoPermissionError, RedisTimeoutError) as exc:
            logger.error(exc)
            return None

    return inner

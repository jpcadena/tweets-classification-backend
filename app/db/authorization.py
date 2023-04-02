"""
Authorization database script
"""
import logging

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
        settings: config.Settings = Depends(config.get_settings)) -> None:
    """
    Init connection to Redis Database
    :param settings: Dependency method for cached setting object
    :type settings: config.Settings
    :return: None
    :rtype: NoneType
    """
    url: str = settings.AIOREDIS_DATABASE_URI
    await aioredis.from_url(url, decode_responses=True)
    logger.info("Redis Database initialized")


def handle_redis_exceptions(func: callable) -> callable:
    """
    Decorator for Redis Exceptions
    :param func: function to be decorated
    :return: return from func or exception raised
    """

    async def inner(*args, **kwargs) -> callable:
        try:
            return await func(*args, **kwargs)
        except AuthenticationError as a_exc:
            logger.error(a_exc)
        except RedisConnectionError as c_exc:
            logger.error(c_exc)
        except DataError as d_exc:
            logger.error(d_exc)
        except NoPermissionError as np_exc:
            logger.error(np_exc)
        except RedisTimeoutError as t_exc:
            logger.error(t_exc)

    return inner

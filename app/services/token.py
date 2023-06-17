"""
Token Service
"""
import logging
from typing import Optional

from aioredis import Redis, RedisError
from fastapi import Depends

from app.api.deps import redis_dependency
from app.core import config
from app.db.authentication import handle_redis_exceptions
from app.models.token import Token

logger: logging.Logger = logging.getLogger(__name__)


class TokenService:
    """
    Service class for token operations in the authentication database
    """

    @staticmethod
    @handle_redis_exceptions
    async def create_token(
            token: Token,
            settings: config.Settings = Depends(config.get_settings),
            redis: Redis = Depends(redis_dependency)
    ) -> bool:
        """
        Create a token in authentication database
        :param token: Token object with key and value
        :type token: Token
        :param settings: Dependency method for cached setting object
        :type settings: config.Settings
        :param redis: Dependency method for async Redis connection
        :type redis: Redis
        :return: True if the token was inserted; otherwise false
        :rtype: bool
        """
        try:
            inserted: bool = await redis.setex(
                token.key, settings.REFRESH_TOKEN_EXPIRE_MINUTES, token.token)
        except RedisError as r_exc:
            logger.error("Error at creating token. %s", r_exc)
            raise r_exc
        return inserted

    @staticmethod
    @handle_redis_exceptions
    async def get_token(
            key: str,
            redis: Redis = Depends(redis_dependency)
    ) -> Optional[str]:
        """
        Read token from the authentication database
        :param key: The key to search for
        :type key: str
        :param redis: Dependency method for async Redis connection
        :type redis: Redis
        :return: The refresh token
        :rtype: str
        """
        try:
            value: str = await redis.get(key)
        except RedisError as r_exc:
            logger.error("Error at getting token. %s", r_exc)
            raise r_exc
        return value

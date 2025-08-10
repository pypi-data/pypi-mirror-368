# -*- coding: utf-8 -*-
from logging import getLogger
from pickle import dumps, loads
from typing import Any, Optional

from aiocache import Cache
from redis.typing import ExpiryT

from vpnflow.services._redis import create_client
from vpnflow.settings import settings

DEFAULT_TTL = settings.cache.default_ttl
logger = getLogger(__name__)
redis_url = settings.cache.redis_url.get_secret_value()

if redis_url:

    class CacheRepository:
        """⭐"""

        client = create_client(redis_url)
        # client.auto_close_connection_pool = True

        @classmethod
        async def get(cls, key: str) -> Optional[Any]:
            """⭐"""
            value = await cls.client.get(key)
            if value is not None:
                try:
                    value = loads(value)
                except TypeError as exc:
                    logger.warning(exc)
                    value = None
            logger.debug(f"Get from cache. Key: {key}. Value: {value}")
            return value

        @classmethod
        async def set(cls, key: str, value: Any, exp: Optional[ExpiryT] = None) -> bool:
            """⭐"""
            logger.debug(f"Set in cache. Key: {key}. Value: {value}. Exp: {exp}")
            await cls.client.set(key, dumps(value), ex=exp)
            return True

        @classmethod
        async def delete(cls, key: str) -> bool:
            """⭐"""
            logger.debug(f"Delete from cache. Key: {key}.")
            await cls.client.delete(key)
            return True

        @classmethod
        async def close(cls) -> bool:
            """⭐"""
            logger.debug("Close cache connection")
            await cls.client.aclose(close_connection_pool=True)
            return True

        @classmethod
        async def check_health(cls) -> bool:
            """⭐"""
            logger.info("Ping cache")
            try:
                r = await cls.client.ping()
                return r
            except Exception as exc:
                logger.error(exc)
                return False

else:

    class CacheRepository:
        """⭐"""

        client = Cache()

        @classmethod
        async def get(cls, key: str) -> Optional[Any]:
            """⭐"""
            value = await cls.client.get(key)
            logger.debug(f"Get from cache. Key: {key}. Value: {value}")
            return value

        @classmethod
        async def set(cls, key: str, value: Any, exp: Optional[ExpiryT] = None) -> bool:
            """⭐"""
            logger.debug(f"Set in cache. Key: {key}. Value: {value}. Exp: {exp}")
            await cls.client.set(key, value, ttl=exp)
            return True

        @classmethod
        async def delete(cls, key: str) -> bool:
            """⭐"""
            logger.debug(f"Delete from cache. Key: {key}.")
            await cls.client.delete(key)
            return True

        @classmethod
        async def close(cls) -> bool:
            """⭐"""
            return True

        @classmethod
        async def check_health(cls) -> bool:
            """⭐"""
            return True

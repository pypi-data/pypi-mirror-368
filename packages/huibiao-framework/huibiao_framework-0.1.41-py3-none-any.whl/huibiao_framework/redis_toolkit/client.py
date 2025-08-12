import redis.asyncio as redis
from typing import Union, Type
from huibiao_framework.config import RedisConfig
from loguru import logger

from huibiao_framework.execption.redis import (
    RedisClientNotInitException,
    RedisClientPingException,
)


class HuibiaoAsyncRedisClientFactory:
    """
    基于redis.asyncio版本的redis客户端工厂，根据配置创建不同模式的Redis客户端
    """

    __client: Union[redis.Redis, redis.RedisCluster] = None

    @classmethod
    def redis_mode(cls):
        if RedisConfig.REDIS_MODE is None:
            return

    @classmethod
    def init_client(cls) -> Type["HuibiaoAsyncRedisClientFactory"]:
        if cls.__client is not None:
            return cls

        logger.debug(f"初始化Redis客户端，模式：{RedisConfig.REDIS_MODE}")

        if RedisConfig.REDIS_MODE.lower() == "single":
            pool = redis.ConnectionPool(
                host=RedisConfig.REDIS_HOST,
                port=RedisConfig.REDIS_PORT,
                db=RedisConfig.REDIS_DB,
                password=RedisConfig.REDIS_PSWD,
            )
            cls.__client = redis.Redis(connection_pool=pool)
            logger.debug(f"Redis客户端初始化完成，连接信息：{pool.connection_kwargs}")

        elif RedisConfig.REDIS_MODE.lower() == "sentinel":
            sentinel = redis.sentinel.Sentinel(
                sentinels=[(RedisConfig.REDIS_HOST, RedisConfig.REDIS_PORT)],
                password=RedisConfig.REDIS_PSWD,
                sentinel_kwargs={"password": RedisConfig.REDIS_SENTINEL_PSWD},
            )
            cls.__client = sentinel.master_for(
                service_name=RedisConfig.REDIS_SENTINEL_SERVICE_NAME,
                db=RedisConfig.REDIS_DB,
            )
            logger.debug(
                f"Redis客户端初始化完成，连接信息：{sentinel.connection_kwargs}"
            )

        elif RedisConfig.REDIS_MODE.lower() == "cluster":
            cls.__client = redis.RedisCluster(
                host=RedisConfig.REDIS_HOST,
                port=RedisConfig.REDIS_PORT,
                password=RedisConfig.REDIS_PSWD,
            )
            logger.debug(
                f"Redis客户端初始化完成，连接信息：{cls.__client.connection_pool.connection_kwargs}"
            )
        else:
            logger.debug(f"Redis模式错误 {RedisConfig.REDIS_MODE}")

        return cls

    @classmethod
    async def ping(cls):
        if cls.__client is not None:
            try:
                await cls.__client.ping()
                logger.debug("Redis客户端连接成功")
            except Exception as e:
                logger.error(f"Redis客户端连接失败：{str(e)}")
                raise RedisClientPingException(e)
        else:
            logger.error("Redis客户端未初始化")
            raise RedisClientNotInitException()

    @classmethod
    def get_client(cls) -> Union[redis.Redis, redis.RedisCluster]:
        cls.init_client()
        return cls.__client

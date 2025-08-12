import asyncio
import time
from typing import Union, Optional
from loguru import logger
import redis.asyncio as redis

from huibiao_framework.execption.redis import RedisLockAcquireTimeOutException
from huibiao_framework.redis_toolkit.client import HuibiaoAsyncRedisClientFactory
from huibiao_framework.utils.annotation import frozen_attrs


@frozen_attrs("lock_key", "lock_value")
class AsyncRedisLock:
    def __init__(
        self,
        lock_key: str,
        lock_value: str,
        *,
        redis_client: Optional[Union[redis.Redis, redis.RedisCluster]] = None,
        expire_time: int = 10,
        acquire_times: int = 30,
        retry_delay: int = 5,
    ):
        self.client = redis_client
        self.lock_key = lock_key
        self.lock_value = lock_value
        self.expire_time = expire_time  # 锁超时时间，秒
        self.acquire_times = acquire_times  # 尝试次数
        self.retry_delay = retry_delay  # 重试间隔，秒

    async def init(self) -> "AsyncRedisLock":
        if self.client is None:
            self.client = await HuibiaoAsyncRedisClientFactory.get_client()
        return self

    async def acquire(self) -> bool:
        """使用 SETNX 原子性获取锁"""
        start_time = time.perf_counter()

        for i in range(self.acquire_times):
            # SET key value NX EX expire 等同于 SETNX + EXPIRE 原子操作
            acquired = await self.client.set(
                self.lock_key,
                self.lock_value,
                nx=True,  # 仅在键不存在时设置（SETNX 效果）
                ex=self.expire_time,  # 设置过期时间，防止死锁 秒
            )
            if acquired:
                logger.debug(
                    f"获取锁成功：{self.lock_key} -> {self.lock_value}, 等待{time.perf_counter() - start_time:.6f}s, 尝试{i + 1}次"
                )
                return True
            if i < self.acquire_times - 1:
                await asyncio.sleep(self.retry_delay)

        logger.warning(
            f"获取锁失败：{self.lock_key} -> {self.lock_value}, 尝试{self.acquire_times}次"
        )
        raise RedisLockAcquireTimeOutException(
            self.lock_key, self.lock_value, time.perf_counter() - start_time
        )

    async def release(self):
        script = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
        """
        result = await self.client.eval(script, 1, self.lock_key, self.lock_value)
        logger.debug(
            f"释放锁成功：{self.lock_key} -> {self.lock_value}, result={result}"
        )

    async def __aenter__(self):
        """支持 async with 语法"""
        return await self.acquire() if self.lock_key else None

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """支持 async with 语法"""
        await self.release()

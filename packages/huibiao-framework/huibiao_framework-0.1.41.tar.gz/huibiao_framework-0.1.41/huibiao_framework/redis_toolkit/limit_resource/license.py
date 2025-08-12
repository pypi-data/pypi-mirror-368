import asyncio
import uuid
from typing import Optional, Union, Dict
import redis.asyncio as redis
from loguru import logger
import time
from pydantic import BaseModel

from huibiao_framework.config.limit_resource import LimitResourceOsConfig
from huibiao_framework.execption.limit_resource import (
    LimitResourceAccessTimeOutException,
)
from huibiao_framework.execption.redis import RedisLockAcquireTimeOutException
from huibiao_framework.redis_toolkit import AsyncRedisLock


class LicenceVo(BaseModel):
    access_time: str  # 首次获取时间
    refresh_time: str  # 刷新时间
    user_info: str


class LimitResourceLicence:
    """
    有限资源访问许可证
    """

    HASH_NAME_REFIX = "huibiao:limit-resource-licence"
    LOCK_KEY_PREFIX = "huibiao:limit-resource-licence-lock"

    def __init__(
        self,
        resource_name: str,
        redis_client: Optional[Union[redis.Redis, redis.RedisCluster]],
        resource_max_num: int,  # 资源最大访问数
        acquire_times: int,  # 尝试次数，获取锁失败不会消耗次数
        retry_delay: int,  # 尝试间隔,秒
        user_info: str = None,
    ):
        assert resource_name, "resource_name is required"
        self.resource_name = resource_name

        self.__while_resource = self.is_while(self.resource_name)

        if self.__while_resource:
            return  # 该资源是被设置为白名单

        assert redis_client, "redis_client is required"
        self.__redis_client = redis_client

        self.resource_max_num = (
            resource_max_num
            if resource_max_num is not None and resource_max_num > 0
            else 16
        )
        self.acquire_times = (
            acquire_times if acquire_times is not None and acquire_times > 0 else 20
        )
        self.retry_delay = (
            retry_delay if retry_delay is not None and retry_delay > 0 else 3
        )
        self.user_info = user_info if user_info else ""

        self.hash_name = self.gen_hash_name(self.resource_name)
        self.hash_key = str(uuid.uuid4())
        self.license_vo = None

        self.locker = AsyncRedisLock(
            redis_client=redis_client,
            lock_key=f"{self.LOCK_KEY_PREFIX}:{resource_name}",
            acquire_times=1,
            lock_value=self.hash_key,  # 动态设置
        )

        logger.debug(
            f"Gen res license [{resource_name}][M={self.resource_max_num}][A={self.acquire_times}][D={self.retry_delay}]"
        )

    def desc(self, used_num=None) -> str:
        description = f"[{self.resource_name}][{self.hash_key}]"
        if self.user_info:
            description += f"[{self.user_info}]"
        if used_num is not None:
            description += f"[{used_num}/{self.resource_max_num}]"
        return description

    @classmethod
    def gen_hash_name(cls, resource_name: str):
        return f"{cls.HASH_NAME_REFIX}:{resource_name}"

    async def get_resource_dict(self) -> Dict[str, str]:
        return await self.__redis_client.hgetall(self.hash_name)

    async def resource_current_used_num(self) -> int:
        """
        资源当前被占用的数量
        """
        return len(await self.get_resource_dict())

    def gen_license_vo(self) -> LicenceVo:
        time_now_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return LicenceVo(
            access_time=time_now_str,
            refresh_time=time_now_str,
            user_info=self.user_info,
        )

    async def acquire(self):
        if self.__while_resource:
            return
        start_time = time.perf_counter()
        i = 1
        while i <= self.acquire_times:
            used_num = await self.resource_current_used_num()
            if used_num >= self.resource_max_num:
                logger.warning(
                    f"{self.desc(used_num)} Resource not enough, try={i}, wait {time.perf_counter() - start_time}s"
                )
                if i < self.acquire_times:
                    await asyncio.sleep(self.retry_delay)
                i += 1
            else:
                is_lock = False
                try:
                    # 资源充足，开始获取锁
                    is_lock = await self.locker.acquire()
                    # 成功获取了锁
                    self.license_vo = self.gen_license_vo()  # 生成vo
                    await self.__redis_client.hset(
                        self.hash_name, self.hash_key, self.license_vo.model_dump_json()
                    )
                    logger.debug(
                        f"{self.desc(used_num)} Get resource success, user_info={self.user_info}, wait {time.perf_counter() - start_time}s, try:{i}"
                    )
                    return  # 结束
                except RedisLockAcquireTimeOutException:
                    logger.warning(f"{self.desc(used_num)} Get resource lock failed. ")
                    if i < self.acquire_times:  # 不是最后一次争抢资源
                        if self.resource_max_num - used_num > 1:
                            await asyncio.sleep(
                                used_num / self.resource_max_num
                            )  # 资源越充足，休眠时间越短
                        else:
                            i += 1
                            await asyncio.sleep(self.retry_delay)
                finally:
                    if is_lock:
                        await self.locker.release()

        waited_time = time.perf_counter() - start_time
        logger.error(
            f"{self.desc()} get resource timeout, wait={waited_time}s, try:{i - 1}"
        )
        assert i - 1 == self.acquire_times
        assert waited_time > self.retry_delay * (self.acquire_times - 1)
        raise LimitResourceAccessTimeOutException(self.resource_name, waited_time)

    async def release(self):
        if self.__while_resource:
            return
        await self.__redis_client.hdel(self.hash_name, self.hash_key)
        logger.debug(f"{self.desc()} Resource release success")

    def is_while(self, resource_name: str):
        # 当前资源是否在白名单中，即无需限制
        return LimitResourceOsConfig.is_while_resource(resource_name)

    async def __aenter__(self):
        """支持 async with 语法"""
        await self.acquire()
        return True

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """支持 async with 语法"""
        await self.release()
        return True

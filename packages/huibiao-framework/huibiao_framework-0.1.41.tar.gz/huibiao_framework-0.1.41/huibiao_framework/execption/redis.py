from .execption import HuiBiaoException


class RedisClientException(HuiBiaoException):
    pass


class RedisClientNotInitException(RedisClientException):
    pass


class RedisClientPingException(RedisClientException):
    def __init__(self, ex: Exception = None):
        self.ex = ex
        super().__init__(str(self.ex))


class RedisLockAcquireTimeOutException(RedisClientException):
    def __init__(self, lock_key: str, lock_value: str, waited_time):
        self.lock_key = lock_key
        self.lock_value = lock_value
        self.waited_time = waited_time
        super().__init__(f"无法获取Redis锁，k={lock_key}, v={lock_value}, {waited_time}秒")
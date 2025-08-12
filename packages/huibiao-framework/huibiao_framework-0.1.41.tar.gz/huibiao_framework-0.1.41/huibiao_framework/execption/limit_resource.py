from .execption import HuiBiaoException


class LimitResourceException(HuiBiaoException):
    pass


class LimitResourceAccessTimeOutException(LimitResourceException):
    def __init__(self, resource_name: str, waited_time):
        self.resource_name = resource_name
        self.waited_time = waited_time
        super().__init__(f"get resource=[{self.resource_name}] timeout, wait={waited_time}s")
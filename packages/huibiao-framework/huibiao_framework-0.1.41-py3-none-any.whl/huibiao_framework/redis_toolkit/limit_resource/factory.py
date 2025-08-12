from enum import Enum

from loguru import logger

from .license import LimitResourceLicence
from huibiao_framework.redis_toolkit.client import HuibiaoAsyncRedisClientFactory
from huibiao_framework.config.limit_resource import LimitResourceOsConfig


class DefaultLimitResourceName(str, Enum):
    HUIZE_QWEN_32B_AWQ = "huizeQwen32bAwq"
    TENDER_IMAGE_OCR = "TenderImageOcr"
    TENDER_LAYOUT_DETECT = "TenderLayoutDetect"


class LimitResourceLicenseFactory:
    @classmethod
    def genLicense(
        cls,
        resource_name: str | DefaultLimitResourceName,
        user_info: str = None,
        max_num: int = None,
        acquire: int = None,
        delay: int = None,
    ) -> LimitResourceLicence:
        """
        获取指定资源的访问限制令牌
        """
        resource_name = (
            resource_name.value
            if isinstance(resource_name, DefaultLimitResourceName)
            else resource_name
        )
        max_num = (
            max_num
            if max_num is not None and max_num > 0
            else LimitResourceOsConfig.get_resource_max_num(resource_name)
        )
        acquire = (
            acquire
            if acquire is not None and acquire > 0
            else LimitResourceOsConfig.get_resource_acq_times(resource_name)
        )
        delay = (
            delay
            if delay is not None and delay > 0
            else LimitResourceOsConfig.get_resource_retry_delay(resource_name)
        )
        return LimitResourceLicence(
            resource_name=resource_name,
            redis_client=HuibiaoAsyncRedisClientFactory.get_client(),
            resource_max_num=max_num,
            acquire_times=acquire,
            retry_delay=delay,
            user_info=user_info,
        )

    @classmethod
    def HuiQwen32bAwqLicense(cls, user_info: str = None):
        return cls.genLicense(
            user_info=user_info,
            resource_name=DefaultLimitResourceName.HUIZE_QWEN_32B_AWQ,
        )

    @classmethod
    def TenderImageOcrLicense(cls, user_info: str = None):
        return cls.genLicense(
            user_info=user_info, resource_name=DefaultLimitResourceName.TENDER_IMAGE_OCR
        )

    @classmethod
    def TenderLayoutDetectLicense(cls, user_info: str = None):
        return cls.genLicense(
            user_info=user_info,
            resource_name=DefaultLimitResourceName.TENDER_LAYOUT_DETECT,
        )

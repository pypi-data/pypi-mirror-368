from functools import wraps
from typing import Callable, Awaitable, TypeVar, Optional, ParamSpec, Union
from .factory import LimitResourceLicenseFactory
from .factory import DefaultLimitResourceName

P = ParamSpec("P")
T = TypeVar("T")


def _limit_resource_license_annotation(
    resource_type: DefaultLimitResourceName,
    user_info: Optional[str] = None,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """
    资源限制许可装饰器，必须带参数使用：@_limit_resource_license_annotation(resource_type=...)

    :param resource_type: 资源类型（必填）
    :param user_info: 可选的用户信息，用于跟踪资源使用
    :return: 装饰器
    """

    def decorator(function: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(function)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            lic = LimitResourceLicenseFactory.genLicense(
                resource_name=resource_type, user_info=user_info
            )
            async with lic:
                return await function(*args, **kwargs)

        return wrapper

    return decorator


def _predefined_license(resource_type: DefaultLimitResourceName):
    """创建支持user_info参数和无括号使用的预定义装饰器"""

    def decorator_or_factory(
        user_info: Optional[Union[str, Callable[P, Awaitable[T]]]] = None,
    ) -> Union[
        Callable[P, Awaitable[T]],
        Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]],
    ]:
        # 处理无参数使用的情况：@huize_qwen32b_awq_license
        if callable(user_info):
            func = user_info
            return _limit_resource_license_annotation(resource_type=resource_type)(func)

        # 处理带user_info参数的情况：@huize_qwen32b_awq_license(user_info="xxx")
        def wrapper(f: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
            return _limit_resource_license_annotation(
                resource_type=resource_type,
                user_info=user_info,  # 可能为None
            )(f)

        return wrapper  # 一个装饰器函数，接收一个异步函数，返回一个新的异步函数，参数和返回类型不变

    return decorator_or_factory


# 预定义Qwen32B AWQ模型的资源许可装饰器
# 支持: @huize_qwen32b_awq_license 或 @huize_qwen32b_awq_license(user_info="xxx")
huize_qwen32b_awq_license = _predefined_license(
    resource_type=DefaultLimitResourceName.HUIZE_QWEN_32B_AWQ
)

# 预定义 tender_image_ocr 资源许可装饰器
tender_image_ocr_license = _predefined_license(
    resource_type=DefaultLimitResourceName.TENDER_IMAGE_OCR
)

# 预定义 tender_layout_detect 模型资源许可装饰器
tender_layout_detect_license = _predefined_license(
    resource_type=DefaultLimitResourceName.TENDER_LAYOUT_DETECT
)

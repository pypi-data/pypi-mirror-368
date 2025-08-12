from .license import LimitResourceLicence
from .factory import LimitResourceLicenseFactory
from .licensee_decorator import (
    huize_qwen32b_awq_license,
    tender_image_ocr_license,
    tender_layout_detect_license,
)

__all__ = [
    "LimitResourceLicence",
    "LimitResourceLicenseFactory",
    "huize_qwen32b_awq_license",
    "tender_image_ocr_license",
    "tender_layout_detect_license",
]

import os
from typing import Dict, List


class LimitResourceOsConfig:
    """
    有限资源访问限制的环境变量配置
    """

    RES_LIMIT_ENABLE: bool = True
    RES_MAX_NUM: int | Dict[str, int] = {}
    RES_ACQ_TIMES: int | Dict[str, int] = {}
    RES_RETRY_DELAY: int | Dict[str, int] = {}
    REST_WHILE_LIST: List[str] = []

    @classmethod
    def init(cls):
        cls.RES_LIMIT_ENABLE = (
            os.getenv("RES_LIMIT_ENABLE", default="True").lower() == "true"
        )
        cls.RES_MAX_NUM = cls.parse_dict(os.getenv("RES_MAX_NUM", default=16))
        cls.RES_ACQ_TIMES = cls.parse_dict(os.getenv("RES_ACQ_TIMES", default=30))
        cls.RES_RETRY_DELAY = cls.parse_dict(os.getenv("RES_RETRY_DELAY", default=5))
        cls.REST_WHILE_LIST = cls.parse_list(os.getenv("REST_WHILE_LIST", default=""))

    @classmethod
    def get_resource_max_num(cls, resource_name: str):
        if isinstance(cls.RES_MAX_NUM, dict):
            return cls.RES_MAX_NUM.get(resource_name)
        else:
            return cls.RES_MAX_NUM

    @classmethod
    def get_resource_acq_times(cls, resource_name: str):
        if isinstance(cls.RES_ACQ_TIMES, dict):
            return cls.RES_ACQ_TIMES.get(resource_name)
        else:
            return cls.RES_ACQ_TIMES

    @classmethod
    def get_resource_retry_delay(cls, resource_name: str):
        if isinstance(cls.RES_RETRY_DELAY, dict):
            return cls.RES_RETRY_DELAY.get(resource_name)
        else:
            return cls.RES_RETRY_DELAY

    @classmethod
    def parse_list(cls, data: str) -> List[str]:
        return [i for i in data.strip().replace(" ", "").split(",") if i]

    @classmethod
    def is_while_resource(cls, resource_name: str):
        return resource_name in cls.REST_WHILE_LIST

    @classmethod
    def parse_dict(cls, data: int | str) -> Dict[str, int] | int:
        """
        解析资源限制字符串为字典

        Args:
            data: 输入字符串，格式为"name1_value1,name2_value2,..."

        Returns:
            返回LimitResourceName到整数值的映射字典

        例如输入："huizeQwen32bAwq_70,TenderImageOcr_50,TenderLayoutDetect_10"
        则返回：{'huizeQwen32bAwq': 70, 'TenderImageOcr': 50, 'TenderLayoutDetect': 10}
        """
        if isinstance(data, int):
            return data

        try:
            int_data = int(data)
            return int_data
        except Exception:
            pass

        result = {}
        if not data or not isinstance(data, str):
            return result

        # 去除空格并按逗号分割
        items = data.strip().replace(" ", "").split(",")
        for item in items:
            if not item and "_" not in item:
                continue

            try:
                res_name, value = item.split("_")  # 只分割第一个下划线
                num_value = int(value)
                result[res_name] = num_value
            except ValueError:
                continue
        return result


LimitResourceOsConfig.init()

import base64
import os
import time
from typing import Optional

import aiohttp
from loguru import logger

from huibiao_framework.client.abstract_client import HuibiaoAbstractClient
from huibiao_framework.config.config import ModelConfig


class ConvertToPdfClient(HuibiaoAbstractClient):
    """
    convert_to_pdf的文件实现类（实例化版本，支持异步请求）
    url: http://host:port/convert
    request:
        file = open(file_path, "rb")
        file_dict = {"File": file}
        data = {"FileName": file_name, "Timeout": 1200}

    response:
        json_data = resp.json()
        pdf_content = base64.b64decode(json_data["result"])
        # 保存为 PDF 文件
        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(pdf_content)
    """

    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        super().__init__(client_name=, session=session, url=ModelConfig.CONVERT_TO_PDF_URL)
        self.CONVERT_TO_PDF_URL =

    async def convert_to_pdf(self, file_path: str, pdf_path: str) -> Optional[str]:
        """发送查询请求到转pdf模型（实例方法）"""

        start_time = time.time()
        try:
            file_name = os.path.basename(file_path)
            file = open(file_path, "rb")
            file_dict = {"File": file}
            data = {"FileName": file_name, "Timeout": 1200}
            # 发送异步POST请求
            async with self.__session.post(
                self.CONVERT_TO_PDF_URL, data=data, files=file_dict
            ) as resp:
                sp_time = time.time() - start_time
                logger.debug(
                    f"ConvertToPdf[{self.session_id}],resp-{resp.status}, 响应时间: {sp_time:.2f}秒"
                )
                resp.raise_for_status()  # 检查HTTP状态码
                response_code = resp.status
                response_data = await resp.json()  # 异步解析JSON
        except aiohttp.ClientError as e:
            logger.error(f"ConvertToPdf[{self.session_id}]请求异常", e)
            raise e
        # 解析响应结果
        code: int = response_code
        if code != 200:
            logger.error(f"ConvertToPdf[{self.session_id}]响应失败，code={code}")
            raise ConvertToPdfResponseCodeError(code)
        if "result" not in response_data:
            logger.error(f"ConvertToPdf[{self.session_id}]响应格式异常, 缺少result字段")
            raise ConvertToPdfResponseFormatError("响应体缺少result字段")

        pdf_content = base64.b64decode(response_data["result"])

        # 保存为 PDF 文件
        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(pdf_content)


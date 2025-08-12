import os
import time
from typing import Optional

import aiohttp
from loguru import logger

from huibiao_framework.client.abstract_client import HuibiaoAbstractClient
from huibiao_framework.config.config import ModelConfig
from huibiao_framework.execption.ocr import (
    DocumentParseResponseCodeError,
    DocumentParseResponseFormatError,
)


class DocumentParseClient(HuibiaoAbstractClient):
    """
    convert_to_pdf的文件实现类
    url: http://host:port/convert
    request:
        params = {
            "FileName": file_name,
            'Dpi': 144,           # 分辨率设置为144 dpi 200dpi，dpi越大精度越高
            'UseFormula': False,  # True/False 是否启用公式识别，启用会增加耗时
            'PdfPwd':'',          # pdf为加密密码
            'PageStart': page_start,       # 开始页码
            'PageCount': page_count,      # 设置解析页数
            'TableFlavor': 'html',  # html/md 表格内容格式 html 或 markdown
            'ParseMode': 'auto',  # auto/scan  设置解析模式为scan模式时会强制进行ocr
            'ImageUpload': False,
            'ImageParse': False,
            }
        headers = {
                    "x-request-id": reqid
                    }

    response:

    """

    def __init__(self, session: Optional[aiohttp.ClientSession]):
        super().__init__(client_name="ConvertToPdf", session=session, url=ModelConfig.DOCUMENT_PARSER_TYY_URL)

    async def convert_to_pdf(
        self,
        pdf_path: str,
        page_count: int,
        page_start: int,
        reqid: str,
        session_id: str = "",
    ) -> Optional[str]:

        session_tag = self.session_tag(session_id)

        start_time = time.time()
        try:
            file_name = os.path.basename(pdf_path)
            file = open(pdf_path, "rb")
            file_dict = {"File": file}
            params = {
                "FileName": file_name,
                "Dpi": 144,  # 分辨率设置为144 dpi 200dpi，dpi越大精度越高
                "UseFormula": False,  # True/False 是否启用公式识别，启用会增加耗时
                "PdfPwd": "",  # pdf为加密密码
                "PageStart": page_start,  # 开始页码
                "PageCount": page_count,  # 设置解析页数
                "TableFlavor": "html",  # html/md 表格内容格式 html 或 markdown
                "ParseMode": "auto",  # auto/scan  设置解析模式为scan模式时会强制进行ocr
                "ImageUpload": False,
                "ImageParse": False,
            }
            headers = {"x-request-id": reqid}
            # 发送异步POST请求
            async with self.__session.post(
                self.url,
                params=params,
                files=file_dict,
                headers=headers,
            ) as resp:
                sp_time = time.time() - start_time
                logger.debug(
                    f"{session_tag},resp-{resp.status}, 响应时间: {sp_time:.2f}秒"
                )
                resp.raise_for_status()  # 检查HTTP状态码
                response_code = resp.status
                response_data = await resp.json()  # 异步解析JSON
        except aiohttp.ClientError as e:
            logger.error(f"{session_tag}请求异常", e)
            raise e
        # 解析响应结果
        code: int = response_code
        if code != 200:
            logger.error(f"{session_tag}响应失败，code={code}")
            raise DocumentParseResponseCodeError(code)
        if "result" not in response_data:
            logger.error(
                f"{session_tag}响应格式异常, 缺少result字段"
            )
            raise DocumentParseResponseFormatError("响应体缺少result字段")

        return response_data["result"]

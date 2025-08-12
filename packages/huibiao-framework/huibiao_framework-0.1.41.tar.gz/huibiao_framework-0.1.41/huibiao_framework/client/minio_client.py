from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import ClientSession
from loguru import logger
from miniopy_async import Minio
from miniopy_async.error import S3Error

from huibiao_framework.config import MinioConfig
from huibiao_framework.execption.minio import (
    MinioClientBucketNotExistsException,
    MinioClientConnectException,
    MinioClientDownloadException,
    MinioClientRemoveObjectException,
    MinioClientUploadException,
)


class MinIOClient:
    def __init__(
        self,
        endpoint: str = MinioConfig.ENDPOINT,
        access_key: str = MinioConfig.AK,
        secret_key: str = MinioConfig.SK,
        secure: bool = MinioConfig.OSS_SECURE,
    ):
        self.__http_client: Optional[ClientSession] = None
        self.__client: Optional[Minio] = None
        self.__endpoint: str = endpoint
        self.__access_key: str = access_key
        self.__secrete_key: str = secret_key
        self.__seccure: bool = secure
        self.__inited = False  # 是否初始化
        self.__is_closed = False  # 实例级别的关闭状态

    @property
    def enabled(self):
        return self.__inited

    async def init(self) -> "MinIOClient":
        if not self.__is_closed:
            self.__http_client = aiohttp.ClientSession()
            self.__client = Minio(
                self.__endpoint,
                access_key=self.__access_key,
                secret_key=self.__secrete_key,
                secure=self.__seccure,
                session=self.__http_client,
            )
            await self.test_connect()
            logger.info(f"MinIO客户端初始化成功: {self.__endpoint}")
            self.__inited = True
        else:
            raise RuntimeError(
                f"MinIO客户端{self.__endpoint}已关闭，无法再使用，请重新创建实例"
            )
        return self

    async def test_connect(self):
        try:
            await self.__client.list_buckets()
        except Exception as e:
            logger.error(f"连接Minios失败: {str(e)}", e)
            raise MinioClientConnectException(str(e))

    async def bucket_exists(self, bucket_name: str) -> bool:
        """检查桶是否存在"""
        try:
            exists = await self.__client.bucket_exists(bucket_name)
            logger.debug(f"桶 {bucket_name} 是否存在: {exists}")
            return exists
        except Exception as e:
            logger.error(f"检查桶 {bucket_name} 存在失败: {e}")
            return False

    async def list_buckets(self) -> List[Dict[str, str]]:
        """列出所有桶"""
        try:
            buckets = await self.__client.list_buckets()
            bucket_list = [
                {"name": bucket.name, "creation_date": str(bucket.creation_date)}
                for bucket in buckets
            ]
            logger.debug(f"获取到 {len(bucket_list)} 个桶")
            return bucket_list
        except Exception as e:
            logger.error(f"列出桶失败: {e}")
            return []

    async def list_objects(
        self, bucket_name: str, prefix: Optional[str] = None, recursive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        列出桶中的对象

        Args:
            bucket_name: 桶名称
            prefix: 对象前缀，用于过滤
            recursive: 是否递归查询

        Returns:
            对象列表，包含名称、大小、修改时间等信息
        """
        try:
            objects = await self.__client.list_objects(
                bucket_name, prefix=prefix, recursive=recursive
            )
            object_list = [
                {
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": str(obj.last_modified),
                    "etag": obj.etag,
                    "content_type": obj.content_type,
                }
                for obj in objects
            ]
            logger.debug(f"桶 {bucket_name} 中列出 {len(object_list)} 个对象")
            return object_list
        except S3Error as e:
            logger.error(f"列出桶 {bucket_name} 中的对象失败: {e}")
            return []

    async def upload_file(self, bucket_name: str, object_name: str, file_path: str):
        """
        上传文件到MinIO

        Args:
            bucket_name: 桶名称
            object_name: 对象名称
            file_path: 本地文件路径

        """
        try:
            # 确保桶存在
            if not await self.bucket_exists(bucket_name):
                raise MinioClientBucketNotExistsException(bucket_name)

            await self.__client.fput_object(bucket_name, object_name, file_path)
            logger.info(f"成功上传文件: {file_path} 到 {bucket_name}/{object_name}")
        except Exception as e:
            logger.error(
                f"上传文件 {file_path} 到 {bucket_name}/{object_name} 失败: {e}"
            )
            raise MinioClientUploadException(str(e))

    async def download_file(self, bucket_name: str, object_name: str, file_path: str):
        """
        从MinIO下载文件

        Args:
            bucket_name: 桶名称
            object_name: 对象名称
            file_path: 本地保存路径
        """
        try:
            await self.__client.fget_object(bucket_name, object_name, file_path)
            logger.info(f"成功下载文件: {bucket_name}/{object_name} 到 {file_path}")
        except Exception as e:
            logger.error(
                f"下载文件 {bucket_name}/{object_name} 到 {file_path} 失败: {e}"
            )
            raise MinioClientDownloadException(str(e))

    async def remove_object(self, bucket_name: str, object_name: str):
        """
        删除对象

        Args:
            bucket_name: 桶名称
            object_name: 对象名称
        """
        try:
            await self.__client.remove_object(bucket_name, object_name)
            logger.info(f"成功删除对象: {bucket_name}/{object_name}")
        except Exception as e:
            logger.error(f"删除对象 {bucket_name}/{object_name} 失败: {e}")
            raise MinioClientRemoveObjectException(str(e))

    async def close(self) -> None:
        """关闭客户端连接及 aiohttp 的 session"""
        if self.__http_client:
            await self.__http_client.close()
            logger.info("Minio aiohttp ClientSession 已关闭")
        self.__http_client = None
        self.__client = None
        self.__is_closed = True
        self.__inited = False

    async def __aenter__(self):
        """异步上下文管理器：进入时初始化会话（实例方法）"""
        await self.init()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器：退出时自动关闭会话（实例方法）"""
        await self.close()

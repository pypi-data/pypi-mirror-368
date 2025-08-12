from .execption import HuiBiaoException


class MinioClientExecution(HuiBiaoException):
    pass


class MinioClientConnectException(MinioClientExecution):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"无法连接到Minio,原因：{reason}")


class MinioClientBucketNotExistsException(MinioClientExecution):
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        super().__init__(f"桶 {bucket_name} 不存在")


class MinioClientOperationExecution(HuiBiaoException):
    pass


class MinioClientUploadException(MinioClientOperationExecution):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"上传文件失败,原因：{reason}")


class MinioClientDownloadException(MinioClientOperationExecution):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"下载文件失败,原因：{reason}")


class MinioClientListBucketsException(MinioClientOperationExecution):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"列出桶失败,原因：{reason}")


class MinioClientRemoveObjectException(MinioClientOperationExecution):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"删除对象失败,原因：{reason}")

from huibiao_framework.utils.meta_class import OsAttrMeta


class TaskConfig(metaclass=OsAttrMeta):
    TASK_RESOURCE_DIR: str = "/task_resource"


class MinioConfig(metaclass=OsAttrMeta):
    ENDPOINT: str
    AK: str
    SK: str
    BUCKET_NAME: str = "huibiao"
    OSS_SECURE: bool = False


class FfcsConfig(metaclass=OsAttrMeta):
    """
    福富后端
    """

    PROGRESS_URL: str = (
        "http://rubikscube.ffcs:8090/product/tenderprogress/taskProgress"
    )
    CALLBACK_URL: str


class RedisConfig(metaclass=OsAttrMeta):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0
    REDIS_PSWD: str
    REDIS_SENTINEL_PSWD: str
    REDIS_SENTINEL_SERVICE_NAME: str = "mymaster"
    REDIS_MODE: str = "single"  # single | cluster | sentinel


class ModelConfig(metaclass=OsAttrMeta):
    REQUEST_URL: str = "http://vllm-qwen-32b.model.hhht.ctcdn.cn:9080/common/query"
    IMAGE_OCR_TYY_URL: str = (
        "http://tender-document-parser.hhht.ctcdn.cn:9080/image_ocr"
    )
    LAYOUT_DETECTION_TYY_URL: str = (
        "http://tender-document-parser.hhht.ctcdn.cn:9080/image_layout"
    )
    DOCUMENT_PARSER_TYY_URL: str
    CONVERT_TO_PDF_URL: str
    EMBED_URL: str = "http://dmx.model.zz.ctcdn.cn:9080/vllm-huize-embedding-zhengwu0329/common/encode"
    CHUNK_URL: str = "http://dmx.model.dev.zz.ctcdn.cn:9080/text-content-chunk-tools-dev/chunk"

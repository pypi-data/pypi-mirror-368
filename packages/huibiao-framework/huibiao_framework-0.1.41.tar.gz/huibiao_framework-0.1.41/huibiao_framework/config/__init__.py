from dotenv import load_dotenv

load_dotenv(".env")

from .config import MinioConfig, TaskConfig, RedisConfig, FfcsConfig

__all__ = ["TaskConfig", "MinioConfig", "RedisConfig", "FfcsConfig"]

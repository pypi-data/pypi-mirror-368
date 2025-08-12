from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

LOG_LEVEL = Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra="allow")

    log_level: LOG_LEVEL = Field(default="INFO", description="日志等级")
    cache_dir: str = Field(default="./cache", description="缓存文件夹位置")
    lru_capacity: int = Field(default=128, description="lru_cache的size")
    adjust: str = Field(default='', description='复权方式')
    genesis_api: str = Field(default="https://genesis.realhuhu.com/", description="Genesis API")
    genesis_token: str = Field(description="Genesis token")


config = Config()

__all__ = ["Config", "config"]

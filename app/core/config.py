from functools import lru_cache
from enum import Enum
from typing import Optional
from starlette.config import Config
from pydantic import BaseSettings

config = Config(".env")


class EnvEnum(str, Enum):
    PROD = "production"
    LOCAL = "local"


class GlobalConfig(BaseSettings):
    DEBUG: bool
    ENV: EnvEnum
    RAW_CT_PATH: str = config("RAW_CT_PATH", default="Path not set")
    DEID_CT_PATH: str = config("DEID_CT_PATH", default="Path not set")
    VIDA_PROCESSED_CT_PATH: str = config(
        "VIDA_PROCESSED_CT_PATH", default="Path not set"
    )
    DB_TABLE_SCAN: str = config("DB_TABLE_SCAN")
    POSTGRES_DB: str = config("POSTGRES_DB")
    POSTGRES_USER: str = config("POSTGRES_USER")
    POSTGRES_PASSWORD: str = config("POSTGRES_PASSWORD")
    DB_URL: str = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@127.0.0.1:5432/{POSTGRES_DB}"

    class Config:
        case_sensitive = True


class LocalConfig(GlobalConfig):
    DEBUG: bool = True
    ENV: EnvEnum = EnvEnum.LOCAL


class ProdConfig(GlobalConfig):
    DEBUG: bool = False
    ENV: EnvEnum = EnvEnum.PROD


class FactoryConfig:
    def __init__(self, environment: Optional[str]):
        self.environment = environment

    def __call__(self) -> GlobalConfig:
        if self.environment == EnvEnum.LOCAL.value:
            return LocalConfig()
        return ProdConfig()


@lru_cache
def get_configuration() -> GlobalConfig:
    return FactoryConfig(config("ENVIRONMENT", default="local"))()


settings = get_configuration()

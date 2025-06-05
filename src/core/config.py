import logging
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

import redis.asyncio as redis

BASE_DIR = Path(__file__).resolve().parent.parent

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s] | %(module)20s:%(lineno)-4d | %(levelname)-8s - %(message)s"
)


class LoggingConfig(BaseModel):
    log_level: Literal[
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    ] = "info"
    log_format: str = LOG_DEFAULT_FORMAT

    @property
    def log_level_value(self) -> int:
        return logging.getLevelNamesMapping()[self.log_level.upper()]


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    max_overflow: int = 10
    pool_size: int = 5

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class Telegram(BaseModel):
    token: str
    admin_chat_id: int


class Parser(BaseModel):
    main_url: str = "https://proverkacheka.com/"


class Uploader(BaseModel):
    DIR: str = Path("/app/shared/uploads")


class Schedule(BaseModel):
    interval: int


class Celery(BaseModel):
    BROKER_URL: str
    RESULT_BACKEND: str


class Redis(BaseModel):
    HOST: str
    PORT: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / ".env.template",
            BASE_DIR / ".env",
        ),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    logging: LoggingConfig = LoggingConfig()
    db: DatabaseConfig
    telegram: Telegram
    parser: Parser = Parser()
    uploader: Uploader = Uploader()
    schedule: Schedule
    celery: Celery
    redis: Redis


settings = Settings()

# Redis
redis_client = redis.Redis(
    host=settings.redis.HOST,
    port=settings.redis.PORT,
    decode_responses=True,  # чтобы не приходилось вручную декодировать строки
)

# Logging
logging.basicConfig(
    level=settings.logging.log_level_value,
    format=settings.logging.log_format,
)

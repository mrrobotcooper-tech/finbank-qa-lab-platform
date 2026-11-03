from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import quote

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


def _discover_env_file() -> Path | None:
    for candidate in Path(__file__).resolve().parents:
        env_path = candidate / ".env"
        if env_path.is_file():
            return env_path
    return None


_REPO_ENV = _discover_env_file()
_ENV_FILES = tuple(path for path in (".env", str(_REPO_ENV) if _REPO_ENV else "") if path)

AppEnv = Literal["dev", "test", "ci", "prod"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILES,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "finbank"
    app_env: AppEnv = "dev"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    worker_port: int = 8001
    public_web_url: str = "http://localhost:5173"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "finbank"
    postgres_user: str = "finbank"
    postgres_password: SecretStr = SecretStr("change_me")

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: SecretStr | None = None

    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "finbank"
    rabbitmq_password: SecretStr = SecretStr("change_me")
    rabbitmq_vhost: str = "/"

    jwt_secret: SecretStr = SecretStr("change_me_jwt")
    jwt_access_ttl_seconds: int = 900
    refresh_ttl_seconds: int = 604800
    login_max_attempts: int = 5
    login_lockout_seconds: int = 900

    correlation_header: str = "X-Correlation-ID"
    finbank_defects: str = ""

    payment_gateway_url: str = "http://localhost:8090"
    notification_gateway_url: str = "http://localhost:8090"

    dependency_timeout_seconds: float = Field(default=2.0, gt=0)

    @property
    def database_url(self) -> str:
        password = self.postgres_password.get_secret_value()
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        if self.redis_password is None or not self.redis_password.get_secret_value():
            return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
        password = self.redis_password.get_secret_value()
        return f"redis://:{password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def rabbitmq_url(self) -> str:
        password = quote(self.rabbitmq_password.get_secret_value(), safe="")
        vhost = quote(self.rabbitmq_vhost, safe="")
        return (
            f"amqp://{self.rabbitmq_user}:{password}"
            f"@{self.rabbitmq_host}:{self.rabbitmq_port}/{vhost}"
        )

    @property
    def is_lab_env(self) -> bool:
        return self.app_env in {"test", "ci"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()

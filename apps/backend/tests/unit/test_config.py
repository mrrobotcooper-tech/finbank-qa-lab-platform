from finbank.core.config import Settings


def test_database_url_uses_asyncpg() -> None:
    settings = Settings(
        postgres_host="postgres",
        postgres_port=5432,
        postgres_db="finbank",
        postgres_user="finbank",
        postgres_password="secret",  # type: ignore[arg-type]
    )
    assert settings.database_url.startswith("postgresql+asyncpg://finbank:secret@postgres:5432/finbank")


def test_lab_env_only_for_test_and_ci() -> None:
    assert Settings(app_env="test").is_lab_env
    assert Settings(app_env="ci").is_lab_env
    assert not Settings(app_env="dev").is_lab_env
    assert not Settings(app_env="prod").is_lab_env


def test_redis_url_includes_password_when_set() -> None:
    settings = Settings(redis_host="redis", redis_password="rpass")  # type: ignore[arg-type]
    assert settings.redis_url == "redis://:rpass@redis:6379/0"


def test_rabbitmq_url_encodes_default_vhost() -> None:
    settings = Settings(
        rabbitmq_host="rabbitmq",
        rabbitmq_user="finbank",
        rabbitmq_password="secret",  # type: ignore[arg-type]
        rabbitmq_vhost="/",
    )
    assert settings.rabbitmq_url == "amqp://finbank:secret@rabbitmq:5672/%2F"

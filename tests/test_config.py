
import pytest
from pydantic import ValidationError

from app.core.config import Settings


def get_valid_settings(**overrides):
    values = {
        "database_url": "postgresql://user:password@localhost/app_db",
        "test_database_url": "postgresql://user:password@localhost/app_test_db",
        "secret_key": "development-secret",
    }

    values.update(overrides)

    return Settings(**values)


def test_default_environment_is_development():
    settings = get_valid_settings()

    assert settings.environment == "development"


def test_log_level_is_normalized():
    settings = get_valid_settings(log_level="info")

    assert settings.log_level == "INFO"


def test_invalid_log_level_is_rejected():
    with pytest.raises(ValidationError):
        get_valid_settings(log_level="INVALID")


def test_invalid_environment_is_rejected():
    with pytest.raises(ValidationError):
        get_valid_settings(environment="staging")


def test_empty_cors_origins_are_rejected():
    with pytest.raises(ValidationError):
        get_valid_settings(cors_origins="")


def test_wildcard_cors_origin_is_rejected():
    with pytest.raises(ValidationError):
        get_valid_settings(cors_origins="*")


def test_production_debug_mode_is_rejected():
    with pytest.raises(ValidationError):
        get_valid_settings(
            environment="production",
            debug=True,
            secret_key="a" * 40,
        )


def test_production_requires_strong_secret():
    with pytest.raises(ValidationError):
        get_valid_settings(
            environment="production",
            debug=False,
            secret_key="short",
        )


def test_production_rejects_localhost_cors():
    with pytest.raises(ValidationError):
        get_valid_settings(
            environment="production",
            debug=False,
            secret_key="a" * 40,
        )


def test_production_configuration_is_valid():
    settings = get_valid_settings(
        environment="production",
        debug=False,
        secret_key="a" * 40,
        cors_origins="https://projectflow.example.com",
    )

    assert settings.environment == "production"
    assert settings.debug is False

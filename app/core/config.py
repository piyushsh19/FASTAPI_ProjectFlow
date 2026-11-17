
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --------------------------------------------------
    # Application
    # --------------------------------------------------

    app_name: str = "ProjectFlow API"
    app_version: str = "0.1.0"
    debug: bool = True

    environment: Literal[
        "development",
        "testing",
        "production",
    ] = "development"

    # --------------------------------------------------
    # Database
    # --------------------------------------------------

    database_url: str
    test_database_url: str | None = None

    # --------------------------------------------------
    # Authentication
    # --------------------------------------------------

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, gt=0)

    # --------------------------------------------------
    # Redis
    # --------------------------------------------------

    redis_url: str = "redis://localhost:6379/0"

    # --------------------------------------------------
    # Logging
    # --------------------------------------------------

    log_level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "DEBUG"

    # --------------------------------------------------
    # CORS
    # --------------------------------------------------

    cors_origins: str = (
        "http://localhost:5173,"
        "http://127.0.0.1:5173"
    )

    # --------------------------------------------------
    # Pydantic Settings
    # --------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --------------------------------------------------
    # Field Validation
    # --------------------------------------------------

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        if isinstance(value, str):
            return value.upper()

        return value

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, value: str) -> str:
        origins = [
            origin.strip()
            for origin in value.split(",")
            if origin.strip()
        ]

        if not origins:
            raise ValueError("At least one CORS origin must be configured")

        for origin in origins:
            if not origin.startswith(("http://", "https://")):
                raise ValueError(
                    f"Invalid CORS origin: {origin}. "
                    "Origins must use HTTP or HTTPS."
                )

            if "*" in origin:
                raise ValueError(
                    "Wildcard CORS origins are not allowed."
                )

        return ",".join(origins)

    # --------------------------------------------------
    # Cross-field Validation
    # --------------------------------------------------

    @model_validator(mode="after")
    def validate_environment_configuration(self):
        if self.environment == "production":
            if self.debug:
                raise ValueError(
                    "DEBUG must be false in production."
                )

            if len(self.secret_key) < 32:
                raise ValueError(
                    "SECRET_KEY must contain at least "
                    "32 characters in production."
                )

            if "localhost" in self.cors_origins:
                raise ValueError(
                    "Production CORS origins must not contain localhost."
                )

        return self

    # --------------------------------------------------
    # Computed Properties
    # --------------------------------------------------

    @property
    def allowed_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()

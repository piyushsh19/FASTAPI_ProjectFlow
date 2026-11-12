
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ProjectFlow API"
    app_version: str = "0.1.0"
    debug: bool = True

    environment: str = "development"

    database_url: str
    test_database_url: str

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    redis_url: str = "redis://localhost:6379/0"

    log_level: str = "DEBUG"

    cors_origins: str = (
        "http://localhost:5173,"
        "http://127.0.0.1:5173"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def allowed_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()

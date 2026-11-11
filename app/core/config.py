
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ProjectFlow API"
    app_version: str = "0.1.0"
    debug: bool = True

    database_url: str
    test_database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
    
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    redis_url: str = "redis://localhost:6379/0"
    log_level: str = "DEBUG"


settings = Settings()

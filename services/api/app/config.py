from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "ORBIT: Autonomous Data Operations Control Tower"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

    # Database & Storage
    DATABASE_URL: str = "postgresql+asyncpg://orbit_admin:orbit_secret_password@localhost:5432/orbit_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    DUCKDB_PATH: str = "./storage/orbit_analytics.duckdb"

    # MLflow
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"

    # Multi-Agent Keys (Optional)
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

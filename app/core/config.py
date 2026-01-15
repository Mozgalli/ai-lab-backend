from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AI LAB Backend"
    env: str = "local"
    secret_key: str = "change-me"

    database_url: str = "postgresql+psycopg://ai:ai@localhost:5432/ai_lab"
    cors_origins: str = "*"

    redis_url: str = "redis://redis:6379/0"
    rq_queue_name: str = "ai_lab"

settings = Settings()

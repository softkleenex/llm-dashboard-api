from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database settings
    db_host: str = "localhost"
    db_port: str = "55554"
    db_service: str = "orclpdb1"
    db_user: str = "llm_admin"
    db_password: str = "comp322"

    # Application settings
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def dsn(self) -> str:
        return f"{self.db_host}:{self.db_port}/{self.db_service}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

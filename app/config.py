from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Database settings - Oracle Cloud (values from environment variables)
    db_user: str = ""  # Set via DB_USER env var
    db_password: str = ""  # Set via DB_PASSWORD env var
    db_dsn: str = ""  # Set via DB_DSN env var
    db_wallet_dir: str = "/app/wallet"  # Default for Cloud Run
    db_wallet_password: str = ""  # Set via DB_WALLET_PASSWORD env var

    # Legacy settings (for backward compatibility)
    db_host: str = "localhost"
    db_port: str = "55554"
    db_service: str = "orclpdb1"

    # Application settings
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def dsn(self) -> str:
        return self.db_dsn

    @property
    def wallet_location(self) -> str:
        return self.db_wallet_dir


@lru_cache()
def get_settings() -> Settings:
    return Settings()

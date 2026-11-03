from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration. Environment variables override safe local defaults."""

    app_name: str = "CareerPilot AI"
    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    frontend_origin: str = "http://localhost:3000"
    ai_provider: str = "none"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = ""
    careerpilot_database_path: str | None = None
    careerpilot_resume_dir: str | None = None
    careerpilot_generated_dir: str | None = None
    gmail_enabled: bool = False
    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    gmail_redirect_uri: str = "http://127.0.0.1:8000/api/v1/gmail/auth/callback"
    gmail_token_path: str = ""
    browser_automation_enabled: bool = False
    browser_profile_dir: str = ""
    application_submission_enabled: bool = False
    google_calendar_enabled: bool = False

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[4] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

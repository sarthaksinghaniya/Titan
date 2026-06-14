"""
Application configuration using Pydantic Settings.
All config values are loaded from environment variables.
"""
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Server ──────────────────────────────────────────────
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DEBUG: bool = True
    API_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # ─── Database ─────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://titan:titanpass@localhost:5432/titan_db"
    DATABASE_ECHO: bool = False

    # ─── Gemini AI ────────────────────────────────────────────
    GEMINI_API_KEY: str = ""
    GEMINI_FLASH_MODEL: str = "gemini-1.5-flash"
    GEMINI_PRO_MODEL: str = "gemini-1.5-pro"
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_MAX_OUTPUT_TOKENS: int = 4096

    # ─── Multi-Model Providers ────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_DEFAULT_MODEL: str = "gpt-4o"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_DEFAULT_MODEL: str = "claude-3-5-sonnet-20240620"
    HUGGINGFACE_API_KEY: str = ""

    # ─── Agent Settings ───────────────────────────────────────
    DEBATE_ROUNDS: int = 2
    MAX_SIMULATION_OPTIONS: int = 3
    AGENT_TIMEOUT_SECONDS: int = 120

    # ─── CORS ─────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: any) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def has_gemini_key(self) -> bool:
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY != "your_gemini_api_key_here")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

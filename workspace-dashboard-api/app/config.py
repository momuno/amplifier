"""
Configuration settings for Workspace Dashboard API
"""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Workspace directory where projects are stored
    workspace_base_dir: Path = Path.home() / "workspaces"

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # CORS settings
    cors_origins: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

# Ensure workspace directory exists
settings.workspace_base_dir.mkdir(parents=True, exist_ok=True)

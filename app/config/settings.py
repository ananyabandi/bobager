"""Application configuration settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Slack API Configuration
    slack_bot_token: str
    slack_user_token: Optional[str] = None  # Required for search.messages API
    slack_app_token: str
    slack_signing_secret: str
    
    # GitHub Configuration
    github_personal_access_token: Optional[str] = None
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    
    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    
    # Cache Configuration
    cache_ttl: int = 3600  # 1 hour
    cache_max_size: int = 1000
    
    # Logging
    log_level: str = "INFO"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


# Global settings instance
settings = Settings(_env_file=".env")  # type: ignore

# Made with Bob

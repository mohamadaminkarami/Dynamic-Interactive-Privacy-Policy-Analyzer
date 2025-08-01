from typing import List, Union

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application Configuration
    API_V1_STR: str = "/api/v1"
    APP_NAME: str = "Dynamic Interactive Decentralized Privacy Policy System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # CORS settings
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",  # Next.js frontend
        "http://localhost:3001",  # Alternative frontend port
        "http://127.0.0.1:3000",
        "http://frontend:3000",   # Docker service name
        "http://172.19.0.1:3000", # Docker gateway
        "http://172.19.0.2:3000", # Docker containers
        "http://172.19.0.3:3000",
        "http://172.19.0.4:3000",
    ]

    # OpenAI / LLM Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL_PRIMARY: str = "gpt-4o"
    OPENAI_MODEL_SECONDARY: str = "gpt-4o-mini"

    # LiteLLM Configuration
    LITELLM_PROXY_URL: str = ""

    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = 50
    REQUEST_TIMEOUT: int = 30

    # Processing Configuration
    MAX_CHUNK_SIZE: int = 4000
    OVERLAP_SIZE: int = 200

    @model_validator(mode="after")
    def check_openai_api_key(self) -> "Settings":
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        return self

    model_config = {
        "extra": "forbid",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }

    DEBUG_LOGGING: bool = True


settings = Settings()

print(settings.model_dump())
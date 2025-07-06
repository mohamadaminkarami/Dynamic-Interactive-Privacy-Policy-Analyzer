import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Privacy Policy Processor"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL_PRIMARY: str = os.getenv("OPENAI_MODEL_PRIMARY", "gpt-4o")
    OPENAI_MODEL_SECONDARY: str = os.getenv("OPENAI_MODEL_SECONDARY", "gpt-4o-mini")
    
    # Application Configuration
    APP_NAME: str = os.getenv("APP_NAME", "Privacy Policy Processor")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "50"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Processing Configuration
    MAX_CHUNK_SIZE: int = int(os.getenv("MAX_CHUNK_SIZE", "4000"))
    OVERLAP_SIZE: int = int(os.getenv("OVERLAP_SIZE", "200"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        return True

# Create global config instance
config = Config() 
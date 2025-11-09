"""
Config loader - reads everything from .env file
Keeps all the settings in one place
"""

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Config(BaseSettings):
    """All app settings"""
    
    # OpenAI settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Serper API for web search (better than DuckDuckGo)
    serper_api_key: str = os.getenv("SERPER_API_KEY", "")
    
    # API server settings
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # Timeout settings (in seconds)
    llm_timeout: int = 30
    search_timeout: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False


config = Config()


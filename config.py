import logging
import sys
from pydantic_settings import BaseSettings, SettingsConfigDict

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

class Settings(BaseSettings):
    VAPI_API_KEY: str
    VAPI_PHONE_NUMBER_ID: str
    VAPI_ASSISTANT_ID: str
    WEBHOOK_URL: str
    
    # Allows falling back to variables loaded from .env and ignores unlisted variables
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

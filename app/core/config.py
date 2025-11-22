from pydantic_settings import BaseSettings
from typing import List, Dict, Any

class Settings(BaseSettings):
    # API Keys
    OPENROUTER_API_KEY: str
    OPENAI_API_KEY: str
    TELEGRAM_BOT_TOKEN: str
    AI_AGENT_KEY: str
    
    # Database
    DATABASE_URL: str
    
    # Application
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Telegram
    WEBHOOK_URL: str = "https://your-domain.com/webhook/telegram"
    
    # Languages
    LANGUAGES_CONFIG: List[Dict[str, str]] = [
        {"name": "English", "code": "en"},
        {"name": "Русский", "code": "ru"},
        {"name": "Қазақша", "code": "kk"},
        {"name": "Кыргызча", "code": "ky"},
        {"name": "O'zbekcha", "code": "uz"},
        {"name": "Українська", "code": "uk"}
    ]
    
    class Config:
        env_file = "/root/bizdna-new/.env"
        case_sensitive = True

settings = Settings()

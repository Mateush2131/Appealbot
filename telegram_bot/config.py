import os
from dataclasses import dataclass, field
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DatabaseConfig:
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", 5432))
    name: str = os.getenv("DB_NAME", "support.db")  # support.db для SQLite
    user: str = os.getenv("DB_USER", "")
    password: str = os.getenv("DB_PASSWORD", "")

@dataclass
class RedisConfig:
    host: str = os.getenv("REDIS_HOST", "localhost")
    port: int = int(os.getenv("REDIS_PORT", 6379))
    db: int = int(os.getenv("REDIS_DB", 0))
    password: Optional[str] = os.getenv("REDIS_PASSWORD")

@dataclass
class APIConfig:
    base_url: str = os.getenv("API_URL", "http://localhost:8000")
    timeout: int = 30
    max_retries: int = 3
    api_key: Optional[str] = os.getenv("API_KEY")

@dataclass
class BotConfig:
    token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    webhook_url: Optional[str] = os.getenv("WEBHOOK_URL")
    webhook_path: str = os.getenv("WEBHOOK_PATH", "/webhook")
    admin_ids: List[int] = field(default_factory=list)
    
    support_chat_id: int = int(os.getenv("SUPPORT_CHAT_ID", "-1001234567890"))
    log_chat_id: int = int(os.getenv("LOG_CHAT_ID", "-1001234567891"))
    
    # Лимиты
    rate_limit: int = 10  # сообщений в минуту
    max_tickets_per_day: int = 20
    max_file_size: int = 10 * 1024 * 1024  # 10 MB
    
    # Фичи
    enable_payments: bool = os.getenv("ENABLE_PAYMENTS", "False").lower() == "true"
    enable_notifications: bool = os.getenv("ENABLE_NOTIFICATIONS", "True").lower() == "true"
    enable_analytics: bool = os.getenv("ENABLE_ANALYTICS", "True").lower() == "true"
    
    def __post_init__(self):
        # Загружаем admin_ids из переменной окружения
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        if admin_ids_str:
            try:
                self.admin_ids = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()]
            except ValueError:
                self.admin_ids = []

@dataclass
class Config:
    bot: BotConfig = field(default_factory=BotConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    api: APIConfig = field(default_factory=APIConfig)
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")

config = Config()
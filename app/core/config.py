import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    # ВАЖНО: Тут должно быть имя сервиса из docker-compose (обычно db или hemoday_db)
    POSTGRES_HOST: str = "db" 
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "hemoday"
    POSTGRES_USER: str = "hemoday"
    POSTGRES_PASSWORD: str = "password"

    # 👇 ДОБАВЬ ВОТ ЭТОТ БЛОК 👇
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = 465
    MAIL_SERVER: str
    MAIL_FROM_NAME: str = "HemoDay"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    # 👆 -------------------- 👆
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def database_url(self) -> str:
        """Construct database URL"""
        return (
            f"postgres://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

settings = Settings()

# Ensure upload directory exists
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# Tortoise-ORM configuration for Aerich
TORTOISE_ORM = {
    "connections": {
        "default": settings.database_url
    },
    "apps": {
        "models": {
            "models": [
                "app.models.user",
                "app.models.family",
                "app.models.transfusion",
                "app.models.reminder",     # Если есть
                "app.models.blood_test",   # Если есть
                "app.models.document",     # Если есть
                "aerich.models",           # Обязательно
                "app.models.password_reset", # <--- ДОБАВЬ ВОТ ЭТУ СТРОКУ
                ],
            "default_connection": "default",
        },
    },
}
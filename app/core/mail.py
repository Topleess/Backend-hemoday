import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from typing import List

# 👇 Импортируем наш главный конфиг (где мы только что прописали поля MAIL_...)
from app.core.config import settings 

# Конфигурация берет данные из settings, а не через os.getenv
# Это надежнее, потому что settings уже проверил, что данные есть.
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
)

async def send_reset_email(email_to: str, token: str):
    """
    Отправляет письмо со ссылкой на сброс пароля
    """
    # Ссылка на сброс (пока локальная)
    reset_link = f"http://localhost:8000/reset-password-page?token={token}"
    
    template_body = {
        "link": reset_link,
        "email": email_to
    }

    message = MessageSchema(
        subject="Восстановление пароля HemoDay",
        recipients=[email_to],
        template_body=template_body,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="email_reset.html")
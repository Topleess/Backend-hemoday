import redis.asyncio as redis
from fastapi_admin.app import app as admin_app
from fastapi_admin.resources import Model, Field, Link, Action
from fastapi_admin.widgets import displays, inputs
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.enums import Method

# Импортируем твои модели
from app.models.user import User
from app.models.family import Family
from app.models.transfusion import Transfusion
# from app.models.blood_test import BloodTest # Раскомментируй по мере готовности

# 1. Настраиваем логику отображения моделей (Resources)

class UserResource(Model):
    label = "Пользователи"
    model = User
    icon = "fas fa-user"
    # Какие поля показывать в списке
    fields = [
        "id",
        "email",
        "family",
        "created_at", # Если есть в WatermelonDBModel
    ]

class FamilyResource(Model):
    label = "Семьи"
    model = Family
    icon = "fas fa-users"
    fields = [
        "id",
        "invite_code",
        "patient_name",
    ]

class TransfusionResource(Model):
    label = "Переливания"
    model = Transfusion
    icon = "fas fa-syringe"
    fields = [
        "id",
        "date",
        "volume_ml",
        "patient_weight_kg",
    ]

# 2. Создаем простой Провайдер Входа (без базы данных, просто хардкод для админа)
class MyAuthProvider(UsernamePasswordProvider):
    async def login(self, username, password):
        # Логин: admin, Пароль: secret
        if username == "admin" and password == "secret":
            return True
        return False

# Инициализируем провайдер
login_provider = MyAuthProvider(
    admin_model=User,  # Это формальность для библиотеки
    login_logo_url="https://preview.tabler.io/static/logo.svg"
)
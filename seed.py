import asyncio
from tortoise import Tortoise
from app.core.config import TORTOISE_ORM
from app.models import User, Family, Transfusion, BloodTest
from faker import Faker
import random
from datetime import timedelta, datetime
from passlib.hash import bcrypt

fake = Faker('ru_RU')

async def seed():
    # Инициализация БД
    await Tortoise.init(config=TORTOISE_ORM)
    
    print("🌱 Начинаем посев данных...")
    
    # Создаем 5 семей
    for _ in range(5):
        family = await Family.create(
            patient_name=fake.name(),
            patient_current_weight=random.randint(50, 90),
            patient_birth_date=fake.date_of_birth(minimum_age=18, maximum_age=60),
            invite_code=fake.bothify(text='??##??').upper()
        )
        print(f"  Created Family: {family.patient_name} ({family.invite_code})")

        # Создаем 1-2 пользователей для семьи
        for _ in range(random.randint(1, 2)):
            await User.create(
                email=fake.email(),
                password_hash=bcrypt.hash("123456"),
                family=family
            )

        # Создаем историю переливаний (5-10 записей)
        for _ in range(random.randint(5, 10)):
            date = fake.date_time_between(start_date='-1y', end_date='now')
            await Transfusion.create(
                family=family,
                date=date,
                volume_ml=random.choice([250, 300, 400, 500]),
                patient_weight_kg=random.randint(50, 90),
                medication_name="Эритроцитарная взвесь",
                value_before=random.randint(60, 90),
                value_after=random.randint(95, 120),
                notes=fake.sentence()
            )

    print("✅ Готово! Данные загружены.")

if __name__ == "__main__":
    asyncio.run(seed())
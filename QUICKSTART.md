# Quick Start Guide

Быстрый старт для разработки и тестирования HemoDay Backend.

## Шаг 1: Клонирование репозитория

```bash
git clone <repository-url>
cd Backend-hemoday
```

## Шаг 2: Настройка окружения

Скопируйте файл с примером переменных окружения:

```bash
copy .env.example .env
```

Для Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

## Шаг 3: Запуск с Docker

Запустите все сервисы:

```bash
docker-compose up -d
```

Дождитесь запуска контейнеров (проверка):

```bash
docker-compose ps
```

## Шаг 4: Инициализация базы данных

Инициализируйте Aerich:

```bash
docker-compose exec api aerich init -t app.core.config.TORTOISE_ORM
```

Создайте первую миграцию:

```bash
docker-compose exec api aerich init-db
```

## Шаг 5: Проверка работы

Откройте в браузере:

- **API Health**: http://localhost:8000/health
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Тестирование API

### 1. Регистрация пользователя

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "patient_name": "Иван Петров",
    "patient_current_weight": 75.5,
    "patient_birth_date": "1990-05-15"
  }'
```

Ответ:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user_id": "uuid",
  "family_id": "uuid",
  "invite_code": "ABC123"
}
```

### 2. Вход в систему

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 3. Получение данных (Pull Sync)

```bash
curl -X GET "http://localhost:8000/api/v1/sync" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Первая синхронизация (все данные):
```bash
curl -X GET "http://localhost:8000/api/v1/sync" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Последующие синхронизации (с timestamp):
```bash
curl -X GET "http://localhost:8000/api/v1/sync?last_pulled_at=1705234567000" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Отправка данных (Push Sync)

```bash
curl -X POST http://localhost:8000/api/v1/sync \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "changes": {
      "transfusions": {
        "created": [
          {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "date": 1705234567000,
            "volume_ml": 450,
            "patient_weight_kg": 75.5,
            "indicator_name": "Hemoglobin",
            "value_before": 85.0,
            "value_after": 95.0,
            "notes": "Первое переливание"
          }
        ],
        "updated": [],
        "deleted": []
      }
    }
  }'
```

### 5. Загрузка файла

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"
```

## Остановка сервисов

```bash
docker-compose down
```

Остановка с удалением данных:

```bash
docker-compose down -v
```

## Использование Makefile (для удобства)

```bash
# Сборка образов
make build

# Запуск сервисов
make up

# Остановка сервисов
make down

# Просмотр логов
make logs

# Миграции
make migrate

# Shell в контейнере API
make shell

# Полная очистка
make clean
```

## Просмотр логов

Все логи:
```bash
docker-compose logs -f
```

Только API:
```bash
docker-compose logs -f api
```

Только база данных:
```bash
docker-compose logs -f db
```

## Подключение к базе данных

```bash
docker-compose exec db psql -U hemoday -d hemoday
```

Полезные SQL команды:

```sql
-- Список таблиц
\dt

-- Список пользователей
SELECT id, email, created_at FROM users;

-- Список семей
SELECT id, invite_code, patient_name FROM families;

-- Список переливаний
SELECT id, date, volume_ml, indicator_name FROM transfusions;
```

## Работа без Docker (локальная разработка)

### 1. Установка uv

```bash
# Windows PowerShell
irm https://astral.sh/uv/install.ps1 | iex
```

### 2. Установка PostgreSQL

Установите PostgreSQL локально или используйте Docker только для БД:

```bash
docker run -d \
  --name hemoday_db \
  -e POSTGRES_USER=hemoday \
  -e POSTGRES_PASSWORD=hemoday \
  -e POSTGRES_DB=hemoday \
  -p 5432:5432 \
  postgres:16-alpine
```

### 3. Установка зависимостей

```bash
uv sync
```

Или с pip:

```bash
pip install -r requirements.txt
```

### 4. Настройка .env

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=hemoday
POSTGRES_USER=hemoday
POSTGRES_PASSWORD=hemoday
```

### 5. Запуск приложения

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Или:

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Troubleshooting

### Ошибка подключения к БД

```bash
# Проверка статуса контейнера
docker-compose ps

# Перезапуск БД
docker-compose restart db

# Проверка логов БД
docker-compose logs db
```

### Порт 8000 уже занят

Измените порт в `docker-compose.yml`:

```yaml
services:
  api:
    ports:
      - "8001:8000"  # Внешний порт 8001
```

### Ошибки миграций

Удалите и пересоздайте миграции:

```bash
docker-compose down -v
docker-compose up -d
docker-compose exec api aerich init -t app.core.config.TORTOISE_ORM
docker-compose exec api aerich init-db
```

## Следующие шаги

1. ✅ Изучите [ARCHITECTURE.md](ARCHITECTURE.md) для понимания архитектуры
2. ✅ Прочитайте [DEPLOYMENT.md](DEPLOYMENT.md) для продакшн развертывания
3. ✅ Используйте Swagger UI (http://localhost:8000/docs) для тестирования API
4. ✅ Интегрируйте с мобильным приложением WatermelonDB

## Полезные ссылки

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tortoise-ORM Documentation](https://tortoise.github.io/)
- [WatermelonDB Sync](https://watermelondb.dev/docs/Sync/Intro)
- [Aerich Documentation](https://github.com/tortoise/aerich)

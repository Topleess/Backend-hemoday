# HemoDay Backend

> Production-ready бэкенд для мобильного приложения "HemoDay" (Дневник переливаний) с архитектурой Offline-First и протоколом синхронизации WatermelonDB.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Tortoise-ORM](https://img.shields.io/badge/Tortoise--ORM-0.21+-orange.svg)](https://tortoise.github.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)

---

## 🚀 Быстрый старт

### Запуск за 3 команды:

```bash
# 1. Запуск сервисов
docker-compose up -d

# 2. Инициализация базы данных
docker-compose exec api aerich init -t app.core.config.TORTOISE_ORM
docker-compose exec api aerich init-db

# 3. Проверка работы
curl http://localhost:8000/health
```

**API доступен по адресу:**
- Health Check: http://localhost:8000/health
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## ✨ Особенности

### 🔄 Offline-First с WatermelonDB
- ✅ Полная поддержка протокола синхронизации WatermelonDB
- ✅ Pull/Push endpoints для инкрементальной синхронизации
- ✅ Soft deletes для сохранения истории изменений
- ✅ Timestamp-based change tracking

### 👨‍👩‍👧‍👦 Семейный доступ
- ✅ Один пациент - несколько пользователей
- ✅ 6-символьные invite коды для присоединения
- ✅ Полная изоляция данных между семьями
- ✅ Общий доступ к медицинским записям

### 🏥 Медицинские данные
- ✅ Записи о переливаниях крови
- ✅ Результаты анализов крови
- ✅ Шаблоны анализов
- ✅ Напоминания о процедурах
- ✅ Загрузка медицинских документов

### 🔐 Безопасность
- ✅ JWT аутентификация
- ✅ bcrypt хеширование паролей
- ✅ Изоляция данных по family_id
- ✅ CORS protection

---

## 📦 Технологический стек

- **Python 3.12** - современный Python с type hints
- **FastAPI** - высокопроизводительный async web framework
- **Tortoise-ORM** - async ORM для PostgreSQL
- **PostgreSQL 16** - надежная реляционная БД
- **Aerich** - инструмент миграций
- **uv** - быстрый package manager от Astral
- **JWT** - stateless аутентификация
- **Docker** - контейнеризация

---

## 📖 Документация

| Документ | Описание |
|----------|----------|
| [📘 QUICKSTART.md](QUICKSTART.md) | Пошаговая инструкция по запуску и тестированию |
| [🧪 API_TESTING_GUIDE.md](API_TESTING_GUIDE.md) | Полное руководство по тестированию API |
| [📐 ARCHITECTURE.md](ARCHITECTURE.md) | Архитектура проекта и технические детали |
| [🚢 DEPLOYMENT.md](DEPLOYMENT.md) | Руководство по production deployment |
| [📝 CHANGELOG.md](CHANGELOG.md) | История изменений |
| [📊 PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Полный обзор проекта |

---

## 🗂️ Структура проекта

```
Backend-hemoday/
├── app/
│   ├── main.py                 # FastAPI приложение
│   ├── models/                 # Tortoise-ORM модели
│   ├── api/v1/                 # API endpoints
│   ├── core/                   # Конфигурация и безопасность
│   └── services/               # Бизнес-логика
├── uploads/                    # Загруженные файлы
├── Dockerfile                  # Docker образ
├── docker-compose.yml          # Multi-container setup
├── pyproject.toml             # uv зависимости
└── Makefile                   # Удобные команды
```

---

## 🔌 API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /register` - Регистрация пользователя (только email + password)
- `POST /login` - Вход в систему
- `POST /join-family` - Присоединение к семье по коду
- `GET /me` - Информация о текущем пользователе
- `POST /password-reset/request` - Восстановление пароля через email

### Synchronization (`/api/v1/sync`)
- `GET /sync?last_pulled_at=<timestamp>` - Pull изменений с сервера
- `POST /sync` - Push изменений на сервер

### File Upload (`/api/v1/upload`)
- `POST /upload` - Загрузка файлов (документы, изображения)

---

## 💾 Модели данных

Все модели включают WatermelonDB обязательные поля:
- `id` (UUID) - первичный ключ
- `created_at` (datetime) - время создания
- `updated_at` (datetime) - время последнего обновления
- `deleted_at` (datetime, nullable) - soft delete маркер

### Основные модели:

- **User** - пользователи с email/password аутентификацией
- **Family** - семьи с уникальными invite кодами
- **Transfusion** - записи о переливаниях крови
- **BloodTest** - события тестирования крови
- **BloodTestResult** - индивидуальные результаты анализов
- **AnalysisTemplate** - пользовательские шаблоны анализов
- **Reminder** - напоминания о процедурах
- **Document** - загруженные документы

---

## 🛠️ Использование с Makefile

```bash
make build    # Собрать Docker образы
make up       # Запустить все сервисы
make down     # Остановить все сервисы
make logs     # Просмотр логов
make migrate  # Запустить миграции
make shell    # Открыть shell в API контейнере
make clean    # Очистить контейнеры и volumes
```

---

## 🧪 Примеры использования API

### Регистрация нового пользователя

**Упрощенная регистрация - только email и password!**

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure123"
  }'
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "family_id": "660e8400-e29b-41d4-a716-446655440001",
  "invite_code": "ABC123"
}
```

### Восстановление пароля

```bash
curl -X POST http://localhost:8000/api/v1/auth/password-reset/request \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

Временный пароль будет отправлен на email (пока выводится в логи сервера).

### Синхронизация данных (Pull)

```bash
curl -X GET "http://localhost:8000/api/v1/sync?last_pulled_at=1705234567000" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Ответ:**
```json
{
  "changes": {
    "transfusions": {
      "created": [...],
      "updated": [...],
      "deleted": ["uuid1", "uuid2"]
    },
    "blood_tests": {...},
    ...
  },
  "timestamp": 1705234890000
}
```

Больше примеров в [API_TESTING_GUIDE.md](API_TESTING_GUIDE.md)

---

## 🔧 Локальная разработка без Docker

### 1. Установка uv

```bash
# Windows PowerShell
irm https://astral.sh/uv/install.ps1 | iex
```

### 2. Установка зависимостей

```bash
uv sync
```

### 3. Запуск PostgreSQL

```bash
docker run -d \
  --name hemoday_db \
  -e POSTGRES_USER=hemoday \
  -e POSTGRES_PASSWORD=hemoday \
  -e POSTGRES_DB=hemoday \
  -p 5432:5432 \
  postgres:16-alpine
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

---

## 🌍 Production Deployment

См. подробное руководство в [DEPLOYMENT.md](DEPLOYMENT.md)

### Основные шаги:

1. Настройте безопасные переменные окружения
2. Используйте managed PostgreSQL сервис
3. Настройте reverse proxy (nginx) с SSL
4. Настройте мониторинг и логирование
5. Настройте автоматические бэкапы

---

## 🔐 Переменные окружения

```env
# Database
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=hemoday
POSTGRES_USER=hemoday
POSTGRES_PASSWORD=your_secure_password

# JWT Authentication
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
```

**Генерация SECRET_KEY:**
```bash
openssl rand -hex 32
```

---

## 📊 Database Schema

```sql
-- Семьи с invite кодами
families (id, invite_code, patient_name, patient_current_weight, ...)

-- Пользователи
users (id, email, password_hash, family_id, ...)

-- Медицинские данные (все с family_id)
transfusions (id, family_id, date, volume_ml, indicator_name, ...)
blood_tests (id, family_id, date, comment, ...)
blood_test_results (id, blood_test_id, family_id, name, value, unit, ...)
analysis_templates (id, family_id, name, indicators_json, ...)
reminders (id, family_id, title, remind_at, frequency, ...)
documents (id, family_id, name, category, file_url, ...)
```

---

## 🧹 Troubleshooting

### Проблемы с запуском

```bash
# Просмотр логов
docker-compose logs -f

# Проверка статуса контейнеров
docker-compose ps

# Перезапуск сервисов
docker-compose restart
```

### Проблемы с миграциями

```bash
# Полная переинициализация
docker-compose down -v
docker-compose up -d
docker-compose exec api aerich init -t app.core.config.TORTOISE_ORM
docker-compose exec api aerich init-db
```

### Проблемы с подключением к БД

```bash
# Проверка БД
docker-compose exec db psql -U hemoday -d hemoday -c "SELECT version();"
```

Больше решений в [QUICKSTART.md](QUICKSTART.md#troubleshooting)

---

## 🎯 Roadmap

### v0.2.0 (Planned)
- [ ] WebSocket для real-time синхронизации
- [ ] Pagination для больших датасетов
- [ ] Full-text search
- [ ] Push notifications
- [ ] Data export (PDF/CSV)

### v0.3.0 (Future)
- [ ] Analytics endpoints
- [ ] S3/CloudFlare R2 integration
- [ ] Rate limiting
- [ ] Audit logging
- [ ] Multi-language support

---

## 📄 License

Proprietary

---

## 👨‍💻 Tech Stack Summary

| Компонент | Технология |
|-----------|-----------|
| Language | Python 3.12 |
| Framework | FastAPI |
| ORM | Tortoise-ORM |
| Database | PostgreSQL 16 |
| Migrations | Aerich |
| Auth | JWT (python-jose) |
| Password | bcrypt (passlib) |
| Package Manager | uv |
| Container | Docker |

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Amazing async web framework
- [Tortoise-ORM](https://tortoise.github.io/) - Async ORM inspired by Django
- [WatermelonDB](https://watermelondb.dev/) - Offline-First sync protocol
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

---

**Status**: ✅ Production Ready

**Version**: 0.1.0

**Developed**: January 2026

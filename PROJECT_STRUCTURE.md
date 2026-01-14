# 🗂️ Project Structure

Полная структура проекта HemoDay Backend с описанием каждого файла и директории.

---

## 📁 Root Level

```
Backend-hemoday/
│
├── 📄 .dockerignore              # Файлы для исключения из Docker образа
├── 📄 .gitignore                 # Файлы для исключения из Git
├── 📄 aerich.ini                 # Конфигурация Aerich (миграции)
├── 📄 docker-compose.yml         # Multi-container orchestration
├── 📄 Dockerfile                 # Docker образ для API
├── 📄 Makefile                   # Удобные команды для разработки
├── 📄 pyproject.toml            # uv зависимости и метаданные
├── 📄 requirements.txt          # Pip fallback зависимости
│
├── 📚 Documentation/
│   ├── 📄 README.md             # Главная документация
│   ├── 📄 ARCHITECTURE.md       # Архитектура проекта
│   ├── 📄 CHANGELOG.md          # История изменений
│   ├── 📄 DEPLOYMENT.md         # Production deployment
│   ├── 📄 FIRST_RUN_CHECKLIST.md # Чек-лист первого запуска
│   ├── 📄 PROJECT_STRUCTURE.md  # Этот файл
│   ├── 📄 PROJECT_SUMMARY.md    # Обзор проекта
│   └── 📄 QUICKSTART.md         # Быстрый старт
│
├── 📁 app/                      # Основной код приложения
├── 📁 uploads/                  # Загруженные файлы
└── 📁 migrations/               # База данных миграции (создается автоматически)
```

---

## 📦 Application Code (`app/`)

```
app/
│
├── 📄 __init__.py               # Python package marker
├── 📄 main.py                   # FastAPI приложение (entry point)
│
├── 📁 models/                   # Tortoise-ORM модели
│   ├── 📄 __init__.py          # Экспорт всех моделей
│   ├── 📄 base.py              # WatermelonDBModel базовый класс
│   ├── 📄 user.py              # User модель
│   ├── 📄 family.py            # Family модель
│   ├── 📄 transfusion.py       # Transfusion модель
│   ├── 📄 blood_test.py        # BloodTest и BloodTestResult модели
│   ├── 📄 analysis_template.py # AnalysisTemplate модель
│   ├── 📄 reminder.py          # Reminder модель
│   └── 📄 document.py          # Document модель
│
├── 📁 api/                      # API endpoints
│   └── 📁 v1/                  # API версия 1
│       ├── 📄 __init__.py
│       ├── 📄 router.py        # Главный роутер (объединяет все endpoints)
│       ├── 📄 schemas.py       # Pydantic схемы (request/response)
│       ├── 📄 auth.py          # Authentication endpoints
│       ├── 📄 sync.py          # Synchronization endpoints
│       └── 📄 upload.py        # File upload endpoint
│
├── 📁 core/                     # Core утилиты
│   ├── 📄 __init__.py
│   ├── 📄 config.py            # Настройки приложения и Tortoise-ORM
│   ├── 📄 security.py          # JWT и password hashing
│   └── 📄 dependencies.py      # FastAPI dependencies (auth)
│
└── 📁 services/                 # Бизнес-логика
    ├── 📄 __init__.py
    └── 📄 sync.py              # WatermelonDB sync service
```

---

## 📊 Detailed File Descriptions

### Root Configuration Files

#### `pyproject.toml`
- **Назначение**: Описание проекта и зависимостей для uv
- **Содержит**:
  - Метаданные проекта (название, версия, описание)
  - Python зависимости
  - Build system конфигурация

#### `requirements.txt`
- **Назначение**: Fallback список зависимостей для pip
- **Использование**: `pip install -r requirements.txt`

#### `aerich.ini`
- **Назначение**: Конфигурация инструмента миграций Aerich
- **Содержит**: Путь к Tortoise-ORM конфигурации и директории миграций

#### `Dockerfile`
- **Назначение**: Определение Docker образа для API
- **Особенности**:
  - Базируется на Python 3.12 slim
  - Использует uv для установки зависимостей
  - Multi-stage build для оптимизации размера

#### `docker-compose.yml`
- **Назначение**: Оркестрация нескольких контейнеров
- **Сервисы**:
  - `db`: PostgreSQL 16
  - `api`: FastAPI приложение
- **Содержит**: Health checks, volumes, networks

#### `Makefile`
- **Назначение**: Удобные команды для разработки
- **Команды**: build, up, down, logs, migrate, shell, clean

---

### Application Core (`app/`)

#### `app/main.py`
**Главный файл приложения**

```python
# Что содержит:
- FastAPI app instance
- CORS middleware
- Tortoise-ORM integration
- API routers
- Health check endpoints
- Lifespan events (startup/shutdown)
```

---

### Models (`app/models/`)

#### `base.py` - Базовая модель
```python
class WatermelonDBModel:
    id: UUID                    # Primary key
    created_at: datetime        # Создание
    updated_at: datetime        # Обновление
    deleted_at: datetime | None # Soft delete
```

#### `user.py` - Пользователь
```python
class User:
    email: str                  # Email (unique)
    password_hash: str          # Хеш пароля
    family_id: UUID             # FK к Family
```

#### `family.py` - Семья
```python
class Family:
    invite_code: str            # 6-символьный код
    patient_name: str           # Имя пациента
    patient_current_weight: float
    patient_birth_date: date
```

#### `transfusion.py` - Переливание
```python
class Transfusion:
    family_id: UUID
    date: datetime
    volume_ml: int
    patient_weight_kg: float
    medication_name: str | None
    indicator_name: str         # Default: "Hemoglobin"
    value_before: float
    value_after: float
    notes: str | None
```

#### `blood_test.py` - Анализы крови
```python
class BloodTest:
    family_id: UUID
    date: datetime
    comment: str | None

class BloodTestResult:
    blood_test_id: UUID         # FK к BloodTest
    family_id: UUID
    name: str                   # Название показателя
    value: float                # Значение
    unit: str                   # Единица измерения
```

#### `analysis_template.py` - Шаблоны анализов
```python
class AnalysisTemplate:
    family_id: UUID
    name: str
    indicators_json: list       # JSON array строк
```

#### `reminder.py` - Напоминания
```python
class Reminder:
    family_id: UUID
    title: str
    remind_at: datetime
    frequency: str
    text: str | None
    is_completed: bool
```

#### `document.py` - Документы
```python
class Document:
    family_id: UUID
    name: str
    category: str | None
    file_url: str               # Путь к файлу
```

---

### API Endpoints (`app/api/v1/`)

#### `schemas.py` - Pydantic схемы
```python
# Authentication
- UserRegister
- UserLogin
- JoinFamily
- Token
- UserResponse

# Synchronization
- SyncPullResponse
- SyncPushRequest
- TableChanges

# File Upload
- FileUploadResponse
```

#### `auth.py` - Аутентификация
```python
POST   /api/v1/auth/register      # Регистрация
POST   /api/v1/auth/login         # Вход
POST   /api/v1/auth/join-family   # Присоединение к семье
GET    /api/v1/auth/me            # Текущий пользователь
```

#### `sync.py` - Синхронизация
```python
GET    /api/v1/sync               # Pull changes
POST   /api/v1/sync               # Push changes
```

#### `upload.py` - Загрузка файлов
```python
POST   /api/v1/upload             # Upload file
```

#### `router.py` - Главный роутер
```python
# Объединяет все роуты из:
- auth.router
- sync.router
- upload.router
```

---

### Core Utilities (`app/core/`)

#### `config.py` - Конфигурация
```python
class Settings:
    # Database
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB
    POSTGRES_USER, POSTGRES_PASSWORD
    
    # JWT
    SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
    
    # File Upload
    UPLOAD_DIR, MAX_FILE_SIZE

TORTOISE_ORM = {
    # Tortoise-ORM конфигурация для Aerich
}
```

#### `security.py` - Безопасность
```python
def verify_password()           # Проверка пароля
def get_password_hash()         # Хеширование пароля
def create_access_token()       # Создание JWT
def decode_access_token()       # Декодирование JWT
```

#### `dependencies.py` - FastAPI зависимости
```python
async def get_current_user()    # Получить текущего пользователя
async def get_current_family_id() # Получить family_id
```

---

### Services (`app/services/`)

#### `sync.py` - Sync Service
```python
class SyncService:
    async def pull_changes()        # Pull от сервера
    async def push_changes()        # Push на сервер
    async def _serialize_record()   # Сериализация
    async def _create_or_update_record()
    async def _soft_delete_record()
```

---

## 📚 Documentation Files

### `README.md`
- **Для кого**: Все пользователи
- **Содержит**: Общее описание, quick start, основные возможности

### `QUICKSTART.md`
- **Для кого**: Разработчики
- **Содержит**: Пошаговые инструкции запуска и тестирования

### `ARCHITECTURE.md`
- **Для кого**: Архитекторы, senior разработчики
- **Содержит**: Архитектура, технические детали, дизайн решения

### `DEPLOYMENT.md`
- **Для кого**: DevOps, администраторы
- **Содержит**: Production deployment, security, scaling

### `FIRST_RUN_CHECKLIST.md`
- **Для кого**: Все
- **Содержит**: Чек-лист проверки работоспособности

### `PROJECT_SUMMARY.md`
- **Для кого**: Менеджеры, Product Owners
- **Содержит**: Обзор проекта, функции, статус

### `CHANGELOG.md`
- **Для кого**: Все
- **Содержит**: История изменений, планы развития

---

## 🔄 Generated/Dynamic Directories

### `migrations/`
- **Создается**: Aerich автоматически
- **Содержит**: SQL миграции базы данных
- **Не в Git**: Да (можно добавить в .gitignore)

### `uploads/`
- **Создается**: При первом запуске
- **Содержит**: Загруженные файлы пользователей
- **Структура**: `uploads/<family_id>/<file_uuid>.<ext>`
- **В Git**: Только .gitkeep

---

## 📊 File Statistics

### Total Files: ~40 файлов

**По типам:**
- Python code: 18 файлов
- Documentation: 8 файлов
- Configuration: 7 файлов
- Docker: 3 файла
- Other: 4 файла

**По директориям:**
- `app/`: 18 файлов
- Root: 14 файлов
- Documentation: 8 файлов

---

## 🎯 Key Features by File

### Authentication Flow
```
main.py → router.py → auth.py → dependencies.py → security.py
                                      ↓
                                   user.py (model)
```

### Sync Flow
```
main.py → router.py → sync.py → services/sync.py
                                      ↓
                              All models (via SYNC_MODELS)
```

### Upload Flow
```
main.py → router.py → upload.py → uploads/ directory
                                      ↓
                                 document.py (model)
```

---

## 🔧 Development Workflow

### 1. Добавление новой модели
```
1. Создать файл в app/models/
2. Наследовать от WatermelonDBModel
3. Добавить в app/models/__init__.py
4. Добавить в TORTOISE_ORM (config.py)
5. Создать миграцию: aerich migrate
6. Применить миграцию: aerich upgrade
```

### 2. Добавление нового endpoint
```
1. Добавить схемы в schemas.py
2. Создать роут в app/api/v1/
3. Добавить в router.py
4. Протестировать через Swagger UI
```

### 3. Добавление нового сервиса
```
1. Создать файл в app/services/
2. Реализовать бизнес-логику
3. Использовать в endpoints
```

---

## 🎓 Learning Path

### Новичкам:
1. README.md → QUICKSTART.md → Swagger UI
2. Изучить модели в app/models/
3. Посмотреть endpoints в app/api/v1/

### Опытным:
1. ARCHITECTURE.md → DEPLOYMENT.md
2. Изучить services/sync.py
3. Посмотреть core/config.py

### DevOps:
1. DEPLOYMENT.md → docker-compose.yml
2. Изучить Dockerfile
3. Настроить production environment

---

## ✅ Checklist для новых разработчиков

- [ ] Прочитал README.md
- [ ] Запустил проект по QUICKSTART.md
- [ ] Протестировал API через Swagger UI
- [ ] Изучил структуру моделей
- [ ] Понял flow синхронизации
- [ ] Знаю как добавить новый endpoint
- [ ] Понимаю систему аутентификации

---

**Структура проекта оптимизирована для:**
- 🚀 Быстрого старта
- 📚 Легкого обучения
- 🔧 Простого расширения
- 🛠️ Удобного обслуживания
- 📦 Production deployment

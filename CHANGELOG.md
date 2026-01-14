# Changelog

All notable changes to HemoDay Backend will be documented in this file.

## [0.1.1] - 2026-01-14

### Changed
- ✅ **Simplified Registration** - теперь для регистрации требуются только `email` и `password`
  - Удалены обязательные поля: `patient_name`, `patient_current_weight`, `patient_birth_date`
  - Модель `Family` обновлена: `patient_name` теперь nullable
  - Данные пациента заполняются из записей о переливаниях крови

### Added
- ✅ **Password Reset System** - система восстановления пароля
  - Новый эндпоинт: `POST /api/v1/auth/password-reset/request`
  - Генерация временного пароля
  - Новая модель: `PasswordResetToken` для отслеживания запросов
  - Подготовка к интеграции с email (пока вывод в логи)
- ✅ **API Testing Guide** - полное руководство по тестированию
  - Документ `API_TESTING_GUIDE.md` с примерами curl
  - Инструкции по использованию Swagger UI
  - Сценарии полного тестирования
  - Примеры семейной синхронизации

### Migration
- ✅ Миграция `1_20260114_update_auth.py`
  - Изменено: `families.patient_name` теперь NULL
  - Создана таблица: `password_reset_tokens`

## [0.1.0] - 2026-01-14

### Added

#### Core Features
- ✅ **WatermelonDB Synchronization Protocol**
  - Pull endpoint with incremental sync
  - Push endpoint with conflict resolution
  - Soft delete support
  - Timestamp-based change tracking

#### Models (Tortoise-ORM)
- ✅ User model with JWT authentication
- ✅ Family model with invite codes
- ✅ Transfusion tracking
- ✅ Blood test events and results
- ✅ Analysis templates (user presets)
- ✅ Reminders with frequency settings
- ✅ Document management with file upload

#### API Endpoints
- ✅ `POST /api/v1/auth/register` - User registration
- ✅ `POST /api/v1/auth/login` - User login
- ✅ `POST /api/v1/auth/join-family` - Join family by code
- ✅ `GET /api/v1/auth/me` - Current user info
- ✅ `GET /api/v1/sync` - Pull changes
- ✅ `POST /api/v1/sync` - Push changes
- ✅ `POST /api/v1/upload` - File upload

#### Infrastructure
- ✅ Docker containerization
- ✅ Docker Compose orchestration
- ✅ PostgreSQL database
- ✅ Aerich migrations
- ✅ uv package management
- ✅ Environment-based configuration

#### Security
- ✅ JWT authentication
- ✅ bcrypt password hashing
- ✅ Family-based data isolation
- ✅ Bearer token authorization
- ✅ CORS protection

#### Documentation
- ✅ README with quick start
- ✅ DEPLOYMENT guide
- ✅ ARCHITECTURE documentation
- ✅ API documentation (Swagger/ReDoc)
- ✅ Makefile with common commands

### Technical Specifications
- Python 3.12
- FastAPI (async web framework)
- Tortoise-ORM (async ORM)
- PostgreSQL 16
- JWT for stateless auth
- Offline-First architecture

## [Unreleased]

### Planned Features
- [ ] WebSocket support for real-time sync
- [ ] Pagination for large datasets
- [ ] Full-text search
- [ ] Push notifications
- [ ] Data export (PDF/CSV)
- [ ] Analytics endpoints
- [ ] S3/CloudFlare R2 integration
- [ ] Rate limiting
- [ ] Audit logging
- [ ] Multi-language support

### Future Improvements
- [ ] Comprehensive test suite
- [ ] Performance monitoring
- [ ] Automated backups
- [ ] CI/CD pipeline
- [ ] API versioning strategy
- [ ] Caching layer (Redis)
- [ ] Background task queue (Celery/ARQ)

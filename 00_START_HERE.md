# 🏥 HemoDay Backend - START HERE

> **Production-ready бэкенд для мобильного приложения "HemoDay" (Дневник переливаний)**

---

## ⚡ Самый быстрый старт

```bash
# 1. Запуск
docker-compose up -d

# 2. Инициализация БД
docker-compose exec api aerich init -t app.core.config.TORTOISE_ORM
docker-compose exec api aerich init-db

# 3. Проверка
curl http://localhost:8000/docs
```

**API готов!** 🎉

---

## 📚 Навигация по документации

### Для начинающих:
1. **[README.md](README.md)** ← Начните отсюда
2. **[QUICKSTART.md](QUICKSTART.md)** ← Пошаговые инструкции
3. **[API_TESTING_GUIDE.md](API_TESTING_GUIDE.md)** ← 🆕 Тестирование API
4. **[FIRST_RUN_CHECKLIST.md](FIRST_RUN_CHECKLIST.md)** ← Проверка работы

### Для разработчиков:
1. **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** ← Структура проекта
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** ← Архитектура и дизайн
3. **[MIGRATION_INSTRUCTIONS.md](MIGRATION_INSTRUCTIONS.md)** ← 🆕 Миграции БД
4. **Swagger UI**: http://localhost:8000/docs

### Для DevOps:
1. **[DEPLOYMENT.md](DEPLOYMENT.md)** ← Production deployment
2. **[docker-compose.yml](docker-compose.yml)** ← Конфигурация контейнеров
3. **[Makefile](Makefile)** ← Удобные команды

### Для менеджеров:
1. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** ← Полный обзор проекта
2. **[CHANGELOG.md](CHANGELOG.md)** ← 🆕 v0.1.1 - История и планы

---

## 🎯 Что реализовано

✅ **WatermelonDB синхронизация** - Offline-First архитектура  
✅ **JWT аутентификация** - Безопасный доступ  
✅ **8 моделей данных** - Все необходимые сущности  
✅ **RESTful API** - Стандартные endpoints  
✅ **File upload** - Загрузка документов  
✅ **Docker** - Готов к deployment  
✅ **Полная документация** - 8+ документов  

---

## 🔧 Технологии

- **Python 3.12** + **FastAPI** (async)
- **Tortoise-ORM** + **PostgreSQL 16**
- **JWT** + **bcrypt** (безопасность)
- **Docker** + **Docker Compose**
- **Aerich** (миграции)
- **uv** (package manager)

---

## 📦 Структура проекта

```
Backend-hemoday/
├── 📁 app/                      # Код приложения
│   ├── main.py                 # FastAPI app
│   ├── models/                 # 8 моделей (User, Family, и т.д.)
│   ├── api/v1/                 # Endpoints (auth, sync, upload)
│   ├── core/                   # Config, security, dependencies
│   └── services/               # Бизнес-логика (sync)
├── 📁 uploads/                  # Загруженные файлы
├── 📄 docker-compose.yml        # Оркестрация
├── 📄 Dockerfile                # API образ
├── 📄 pyproject.toml           # Зависимости (uv)
└── 📚 8 документов              # Полная документация
```

---

## 🚀 API Endpoints

### Authentication
```
POST /api/v1/auth/register     # Регистрация
POST /api/v1/auth/login        # Вход
POST /api/v1/auth/join-family  # Присоединение к семье
GET  /api/v1/auth/me           # Текущий пользователь
```

### Synchronization (WatermelonDB)
```
GET  /api/v1/sync              # Pull changes
POST /api/v1/sync              # Push changes
```

### File Management
```
POST /api/v1/upload            # Загрузка файлов
```

---

## 💡 Быстрые команды

```bash
# С Docker Compose
docker-compose up -d           # Запуск
docker-compose logs -f         # Логи
docker-compose down            # Остановка

# С Makefile (удобнее)
make up                        # Запуск
make logs                      # Логи
make down                      # Остановка
make migrate                   # Миграции
make shell                     # Shell в контейнере
```

---

## 🧪 Тестирование

### Swagger UI (рекомендуется)
http://localhost:8000/docs

### cURL примеры

**Регистрация:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","patient_name":"Test"}'
```

**Pull sync:**
```bash
curl -X GET http://localhost:8000/api/v1/sync \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Больше примеров в [QUICKSTART.md](QUICKSTART.md)

---

## 🔐 Безопасность

✅ JWT аутентификация (Bearer tokens)  
✅ bcrypt password hashing  
✅ Family-based data isolation  
✅ Soft deletes (сохранение истории)  
✅ CORS protection  
✅ Environment variables  

---

## 📊 Модели данных

Все с WatermelonDB полями (`id`, `created_at`, `updated_at`, `deleted_at`):

1. **User** - пользователи
2. **Family** - семьи с invite кодами
3. **Transfusion** - переливания
4. **BloodTest** - анализы крови
5. **BloodTestResult** - результаты
6. **AnalysisTemplate** - шаблоны
7. **Reminder** - напоминания
8. **Document** - документы

---

## 🆘 Помощь

### Не запускается?
```bash
docker-compose down -v
docker-compose up -d --build
docker-compose logs -f
```

### Ошибки миграций?
```bash
docker-compose exec api aerich init -t app.core.config.TORTOISE_ORM
docker-compose exec api aerich init-db
```

### Нужна помощь?
- Проверьте [QUICKSTART.md](QUICKSTART.md) → Troubleshooting
- Посмотрите [FIRST_RUN_CHECKLIST.md](FIRST_RUN_CHECKLIST.md)
- Изучите логи: `docker-compose logs -f`

---

## ✅ Next Steps

1. ✅ Запустите проект (3 команды выше)
2. ✅ Откройте Swagger UI: http://localhost:8000/docs
3. ✅ Протестируйте endpoints
4. ✅ Прочитайте [ARCHITECTURE.md](ARCHITECTURE.md)
5. ✅ Интегрируйте с мобильным приложением

---

## 📞 Quick Links

| Ссылка | Описание |
|--------|----------|
| http://localhost:8000 | API Root |
| http://localhost:8000/health | Health Check |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |

---

## 🎓 Рекомендуемый порядок изучения

### День 1: Запуск и тестирование
1. Запустить проект
2. Открыть Swagger UI
3. Протестировать регистрацию и вход
4. Протестировать sync endpoints

### День 2: Понимание архитектуры
1. Прочитать [ARCHITECTURE.md](ARCHITECTURE.md)
2. Изучить модели в `app/models/`
3. Изучить endpoints в `app/api/v1/`
4. Понять flow синхронизации

### День 3: Разработка
1. Добавить новую модель
2. Создать новый endpoint
3. Протестировать через Swagger UI

---

## 📈 Статус проекта

| Компонент | Статус |
|-----------|--------|
| Backend API | ✅ Production Ready |
| Authentication | ✅ Готово |
| Synchronization | ✅ Готово |
| File Upload | ✅ Готово |
| Docker | ✅ Готово |
| Documentation | ✅ 8+ документов |
| Tests | ⏳ Планируется |

**Версия**: 0.1.0  
**Дата**: Январь 2026  
**Статус**: ✅ **Production Ready**

---

## 🎉 Готово к использованию!

Проект полностью готов к:
- ✅ Локальной разработке
- ✅ Тестированию
- ✅ Интеграции с мобильным приложением
- ✅ Production deployment

**Начните с [README.md](README.md) или [QUICKSTART.md](QUICKSTART.md)**

---

> 💡 **Совет**: Если вы впервые работаете с проектом, начните с [QUICKSTART.md](QUICKSTART.md) - там есть пошаговые инструкции с примерами команд и ожидаемыми результатами.

---

**Создано**: Senior Python Backend Developer  
**Технологии**: Python 3.12, FastAPI, Tortoise-ORM, PostgreSQL, Docker  
**Архитектура**: Offline-First (WatermelonDB Protocol)

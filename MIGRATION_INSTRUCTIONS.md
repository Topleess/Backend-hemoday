# 🔄 Инструкции по применению миграций

## Обновление до версии 0.1.1

Версия 0.1.1 включает важные изменения в схеме базы данных:
1. Упрощенная регистрация - `patient_name` теперь опциональное поле
2. Новая таблица `password_reset_tokens` для восстановления пароля

### Применение миграций

#### Если используете Docker (рекомендуется):

```bash
# 1. Остановите контейнеры
docker-compose down

# 2. Запустите контейнеры
docker-compose up -d

# 3. Примените миграцию
docker-compose exec backend aerich upgrade

# 4. Проверьте статус
docker-compose exec backend aerich history
```

#### Если используете локальную установку:

```bash
# 1. Убедитесь, что PostgreSQL запущен
# 2. Примените миграцию
uv run aerich upgrade

# 3. Проверьте статус
uv run aerich history
```

### Проверка успешного применения

После применения миграции выполните:

```bash
# Проверьте структуру таблицы families
docker-compose exec postgres psql -U postgres -d hemoday -c "\d families"

# Проверьте наличие таблицы password_reset_tokens
docker-compose exec postgres psql -U postgres -d hemoday -c "\d password_reset_tokens"
```

**Ожидаемый результат:**
- В таблице `families` поле `patient_name` должно быть `nullable`
- Должна существовать таблица `password_reset_tokens` с полями:
  - `id` (SERIAL)
  - `token` (VARCHAR(64), UNIQUE)
  - `expires_at` (TIMESTAMPTZ)
  - `used` (BOOL)
  - `created_at` (TIMESTAMPTZ)
  - `user_id` (UUID, FK to users)

### Откат миграции (если необходимо)

```bash
# ВНИМАНИЕ: Откат удалит таблицу password_reset_tokens!
docker-compose exec backend aerich downgrade

# Если в таблице families есть записи с NULL в patient_name,
# откат может завершиться ошибкой
```

### Устранение проблем

**Проблема:** Миграция не применяется

```bash
# Проверьте логи
docker-compose logs backend

# Проверьте подключение к БД
docker-compose exec postgres psql -U postgres -d hemoday -c "SELECT version();"
```

**Проблема:** Ошибка "aerich not found"

```bash
# Пересоберите контейнер
docker-compose build backend
docker-compose up -d backend
```

**Проблема:** Существующие записи с NULL patient_name

Это нормально и ожидаемо! Новая логика позволяет создавать семьи без имени пациента.

### Тестирование после миграции

```bash
# 1. Проверьте health endpoint
curl http://localhost:8000/health

# 2. Протестируйте новую регистрацию
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# 3. Протестируйте восстановление пароля
curl -X POST "http://localhost:8000/api/v1/auth/password-reset/request" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }'

# 4. Проверьте логи для временного пароля
docker-compose logs -f backend | grep "Password reset"
```

---

## Создание новых миграций (для разработчиков)

### Автоматическое создание миграции:

```bash
# 1. Измените модели в app/models/
# 2. Создайте миграцию
docker-compose exec backend aerich migrate --name "description_of_changes"

# 3. Просмотрите созданную миграцию
cat migrations/models/*.py

# 4. Примените миграцию
docker-compose exec backend aerich upgrade
```

### Ручное создание миграции:

Создайте файл `migrations/models/X_YYYYMMDD_name.py`:

```python
from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- Ваши SQL команды здесь
        ALTER TABLE "table_name" ADD COLUMN "new_column" VARCHAR(255);
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- SQL для отката
        ALTER TABLE "table_name" DROP COLUMN "new_column";
    """
```

---

## История миграций

- `0_20260114114539_init.py` - Начальная миграция (v0.1.0)
  - Создание всех таблиц
  - Настройка constraints и индексов

- `1_20260114_update_auth.py` - Обновление аутентификации (v0.1.1)
  - `families.patient_name` → nullable
  - Создание `password_reset_tokens`

---

**Важно:** Всегда делайте резервную копию базы данных перед применением миграций в production!

```bash
# Бэкап БД
docker-compose exec postgres pg_dump -U postgres hemoday > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление из бэкапа
docker-compose exec -T postgres psql -U postgres hemoday < backup_20260114_120000.sql
```

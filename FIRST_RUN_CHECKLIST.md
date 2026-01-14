# 🚀 First Run Checklist

## Проверочный чек-лист первого запуска HemoDay Backend

Используйте этот чек-лист для проверки успешного развертывания проекта.

---

## ✅ Pre-Flight Check

### 1. Требования
- [ ] Docker установлен (версия 20+)
- [ ] Docker Compose установлен (версия 2.0+)
- [ ] Порты 8000 и 5432 свободны
- [ ] Минимум 2GB свободной RAM

### 2. Файлы проекта
- [ ] Все файлы из репозитория скопированы
- [ ] Файл `.env` создан (можно скопировать из `.env.example`)
- [ ] Директория `uploads/` существует

---

## 🏗️ Installation Steps

### Шаг 1: Запуск сервисов

```bash
cd Backend-hemoday
docker-compose up -d
```

**Ожидаемый результат:**
```
✔ Network backend-hemoday_default  Created
✔ Container hemoday_db              Started
✔ Container hemoday_api             Started
```

**Проверка:**
```bash
docker-compose ps
```

Должны быть 2 контейнера в статусе "Up":
- `hemoday_db` (PostgreSQL)
- `hemoday_api` (FastAPI)

---

### Шаг 2: Инициализация базы данных

```bash
docker-compose exec api aerich init -t app.core.config.TORTOISE_ORM
```

**Ожидаемый результат:**
```
Success create migrate location migrations
Success write config to aerich.ini
```

```bash
docker-compose exec api aerich init-db
```

**Ожидаемый результат:**
```
Success create app migrate location migrations\models
Success generate schema for app "models"
```

---

### Шаг 3: Проверка работы API

#### 3.1 Health Check

```bash
curl http://localhost:8000/health
```

**Ожидаемый ответ:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

#### 3.2 Root Endpoint

```bash
curl http://localhost:8000/
```

**Ожидаемый ответ:**
```json
{
  "status": "ok",
  "service": "HemoDay API",
  "version": "1.0.0"
}
```

#### 3.3 Swagger Documentation

Откройте в браузере: http://localhost:8000/docs

**Должна открыться интерактивная документация API**

---

## 🧪 Functional Testing

### Test 1: Регистрация пользователя

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456",
    "patient_name": "Test Patient"
  }'
```

**Проверка результата:**
- [ ] Статус ответа: 201 Created
- [ ] В ответе присутствует `access_token`
- [ ] В ответе присутствует `user_id` (UUID)
- [ ] В ответе присутствует `family_id` (UUID)
- [ ] В ответе присутствует `invite_code` (6 символов)

**Сохраните токен из ответа для следующих тестов!**

```bash
# Пример (замените на ваш токен)
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### Test 2: Вход в систему

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456"
  }'
```

**Проверка результата:**
- [ ] Статус ответа: 200 OK
- [ ] Получен тот же `user_id` что и при регистрации
- [ ] Получен новый `access_token`

---

### Test 3: Получение информации о пользователе

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Проверка результата:**
- [ ] Статус ответа: 200 OK
- [ ] В ответе email: "test@example.com"
- [ ] Присутствует `family_id`

---

### Test 4: Pull синхронизация (первый раз)

```bash
curl -X GET http://localhost:8000/api/v1/sync \
  -H "Authorization: Bearer $TOKEN"
```

**Проверка результата:**
- [ ] Статус ответа: 200 OK
- [ ] В ответе присутствует объект `changes`
- [ ] В `changes` есть все таблицы (transfusions, blood_tests, и т.д.)
- [ ] Все массивы `created`, `updated`, `deleted` пустые (первая синхронизация)
- [ ] Присутствует `timestamp` (число)

---

### Test 5: Push синхронизация (создание записи)

```bash
curl -X POST http://localhost:8000/api/v1/sync \
  -H "Authorization: Bearer $TOKEN" \
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
            "notes": "Test transfusion",
            "created_at": 1705234567000,
            "updated_at": 1705234567000
          }
        ],
        "updated": [],
        "deleted": []
      }
    }
  }'
```

**Проверка результата:**
- [ ] Статус ответа: 200 OK
- [ ] В ответе: `{"status": "ok"}`

---

### Test 6: Pull синхронизация (проверка созданной записи)

```bash
curl -X GET http://localhost:8000/api/v1/sync \
  -H "Authorization: Bearer $TOKEN"
```

**Проверка результата:**
- [ ] В `changes.transfusions.created` присутствует 1 запись
- [ ] ID записи: "550e8400-e29b-41d4-a716-446655440000"
- [ ] Все поля заполнены корректно

---

### Test 7: Загрузка файла

Создайте тестовый файл:

```bash
# Windows PowerShell
"Test document content" | Out-File -FilePath test.txt -Encoding utf8
```

Загрузите файл:

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.txt"
```

**Проверка результата:**
- [ ] Статус ответа: 201 Created
- [ ] В ответе присутствует `file_url`
- [ ] В ответе присутствует `filename`
- [ ] В ответе присутствует `size`
- [ ] Файл сохранен в `uploads/<family_id>/`

Проверьте наличие файла:

```bash
ls uploads/
```

---

## 🔍 Database Verification

### Проверка созданных таблиц

```bash
docker-compose exec db psql -U hemoday -d hemoday -c "\dt"
```

**Ожидаемые таблицы:**
- [ ] `aerich`
- [ ] `analysis_templates`
- [ ] `blood_test_results`
- [ ] `blood_tests`
- [ ] `documents`
- [ ] `families`
- [ ] `reminders`
- [ ] `transfusions`
- [ ] `users`

---

### Проверка данных

```bash
# Пользователи
docker-compose exec db psql -U hemoday -d hemoday -c "SELECT id, email FROM users;"

# Семьи
docker-compose exec db psql -U hemoday -d hemoday -c "SELECT id, invite_code, patient_name FROM families;"

# Переливания
docker-compose exec db psql -U hemoday -d hemoday -c "SELECT id, volume_ml, indicator_name FROM transfusions;"
```

**Проверка результата:**
- [ ] Есть 1 пользователь (test@example.com)
- [ ] Есть 1 семья с invite кодом
- [ ] Есть 1 запись о переливании

---

## 📊 Logs Verification

### Проверка логов API

```bash
docker-compose logs api
```

**Что проверить:**
- [ ] Нет ошибок при запуске
- [ ] Tortoise-ORM успешно подключен к БД
- [ ] Все роуты зарегистрированы
- [ ] Все запросы логируются

---

### Проверка логов БД

```bash
docker-compose logs db
```

**Что проверить:**
- [ ] PostgreSQL запустился успешно
- [ ] База данных создана
- [ ] Нет ошибок подключения

---

## 🎯 Final Checklist

### Backend
- [ ] ✅ API запущен и отвечает на запросы
- [ ] ✅ Swagger UI доступен
- [ ] ✅ База данных инициализирована
- [ ] ✅ Таблицы созданы

### Authentication
- [ ] ✅ Регистрация работает
- [ ] ✅ Вход работает
- [ ] ✅ JWT токены выдаются
- [ ] ✅ Защищенные endpoints требуют авторизацию

### Synchronization
- [ ] ✅ Pull sync работает
- [ ] ✅ Push sync работает
- [ ] ✅ Данные сохраняются в БД
- [ ] ✅ Timestamp tracking работает

### File Upload
- [ ] ✅ Файлы загружаются
- [ ] ✅ Файлы сохраняются в uploads/
- [ ] ✅ File URL возвращается

### Data Isolation
- [ ] ✅ Пользователи привязаны к семьям
- [ ] ✅ Данные изолированы по family_id
- [ ] ✅ Invite коды работают

---

## 🚨 Common Issues

### Issue: Контейнеры не запускаются

**Решение:**
```bash
docker-compose down
docker-compose up -d --build
```

### Issue: Порт 8000 занят

**Решение:** Измените порт в `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"
```

### Issue: Ошибки миграций

**Решение:**
```bash
docker-compose down -v  # Удалить volumes
docker-compose up -d
docker-compose exec api aerich init -t app.core.config.TORTOISE_ORM
docker-compose exec api aerich init-db
```

### Issue: JWT токен не работает

**Проверка:**
1. Токен копируется полностью
2. Используется формат: `Bearer <token>`
3. SECRET_KEY не изменился

---

## ✅ Success Criteria

Если все пункты выполнены, ваш backend готов к работе:

- ✅ Все сервисы запущены
- ✅ API отвечает на запросы
- ✅ Аутентификация работает
- ✅ Синхронизация работает
- ✅ Файлы загружаются
- ✅ Данные сохраняются в БД

---

## 🎓 Next Steps

1. **Интеграция с мобильным приложением**
   - Используйте полученный токен для запросов
   - Реализуйте WatermelonDB sync на клиенте
   - Тестируйте offline режим

2. **Production deployment**
   - Следуйте инструкциям в [DEPLOYMENT.md](DEPLOYMENT.md)
   - Настройте SSL/HTTPS
   - Настройте мониторинг

3. **Разработка новых функций**
   - Изучите [ARCHITECTURE.md](ARCHITECTURE.md)
   - Добавьте новые endpoints по необходимости
   - Создайте миграции для новых таблиц

---

## 📞 Support

При возникновении проблем:

1. Проверьте логи: `docker-compose logs -f`
2. Посмотрите [QUICKSTART.md](QUICKSTART.md)
3. Изучите [ARCHITECTURE.md](ARCHITECTURE.md)
4. Проверьте Swagger UI: http://localhost:8000/docs

---

**Congratulations! 🎉**

Ваш HemoDay Backend успешно развернут и готов к работе!

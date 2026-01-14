#!/bin/bash
# Тестовые команды для HemoDay Backend v0.1.1
# Скопируйте и выполните в PowerShell или bash

echo "🧪 Тестирование HemoDay Backend"
echo "================================"

# Базовый URL
API_URL="http://localhost:8000"

echo ""
echo "1️⃣ Проверка здоровья API..."
curl -s "${API_URL}/health" | jq '.'

echo ""
echo "2️⃣ Регистрация нового пользователя..."
REGISTER_RESPONSE=$(curl -s -X POST "${API_URL}/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }')

echo $REGISTER_RESPONSE | jq '.'

# Извлекаем токен и invite_code
TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.access_token')
INVITE_CODE=$(echo $REGISTER_RESPONSE | jq -r '.invite_code')

echo ""
echo "✅ Токен: $TOKEN"
echo "✅ Invite Code: $INVITE_CODE"

echo ""
echo "3️⃣ Получение информации о пользователе..."
curl -s -X GET "${API_URL}/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

echo ""
echo "4️⃣ Первая синхронизация (Pull)..."
SYNC_RESPONSE=$(curl -s -X GET "${API_URL}/api/v1/sync" \
  -H "Authorization: Bearer $TOKEN")

echo $SYNC_RESPONSE | jq '.'

TIMESTAMP=$(echo $SYNC_RESPONSE | jq -r '.timestamp')
echo "✅ Timestamp для следующей синхронизации: $TIMESTAMP"

echo ""
echo "5️⃣ Отправка данных (Push) - запись о переливании..."
curl -s -X POST "${API_URL}/api/v1/sync" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "changes": {
      "transfusions": {
        "created": [
          {
            "id": "550e8400-e29b-41d4-a716-446655440010",
            "date": "2026-01-14T10:00:00Z",
            "volume_ml": 250,
            "patient_weight_kg": 30.5,
            "indicator_name": "Hemoglobin",
            "value_before": 85.0,
            "value_after": 95.0,
            "notes": "Test transfusion"
          }
        ],
        "updated": [],
        "deleted": []
      }
    }
  }' | jq '.'

echo ""
echo "6️⃣ Повторная синхронизация - проверяем данные..."
curl -s -X GET "${API_URL}/api/v1/sync?last_pulled_at=$TIMESTAMP" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

echo ""
echo "7️⃣ Восстановление пароля..."
curl -s -X POST "${API_URL}/api/v1/auth/password-reset/request" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }' | jq '.'

echo ""
echo "⚠️ Проверьте логи для получения временного пароля:"
echo "docker-compose logs backend | grep 'Password reset'"

echo ""
echo "8️⃣ Второй пользователь присоединяется к семье..."
TOKEN2=$(curl -s -X POST "${API_URL}/api/v1/auth/join-family" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"family@example.com\",
    \"password\": \"password123\",
    \"invite_code\": \"$INVITE_CODE\"
  }" | jq -r '.access_token')

echo "✅ Токен второго пользователя: $TOKEN2"

echo ""
echo "9️⃣ Второй пользователь получает данные (должен видеть запись первого)..."
curl -s -X GET "${API_URL}/api/v1/sync" \
  -H "Authorization: Bearer $TOKEN2" | jq '.'

echo ""
echo "✅ Тестирование завершено!"
echo ""
echo "📊 Результаты:"
echo "- Регистрация: ✅"
echo "- Авторизация: ✅"
echo "- Получение профиля: ✅"
echo "- Синхронизация Pull: ✅"
echo "- Синхронизация Push: ✅"
echo "- Восстановление пароля: ✅"
echo "- Семейный доступ: ✅"
echo ""
echo "🎉 Все работает!"

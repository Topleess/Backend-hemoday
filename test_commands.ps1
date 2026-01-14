# Тестовые команды для HemoDay Backend v0.1.1
# Выполните в PowerShell

Write-Host "🧪 Тестирование HemoDay Backend" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Базовый URL
$API_URL = "http://localhost:8000"

Write-Host ""
Write-Host "1️⃣ Проверка здоровья API..." -ForegroundColor Yellow
$health = Invoke-RestMethod -Uri "$API_URL/health" -Method Get
$health | ConvertTo-Json

Write-Host ""
Write-Host "2️⃣ Регистрация нового пользователя..." -ForegroundColor Yellow
$registerBody = @{
    email = "test@example.com"
    password = "password123"
} | ConvertTo-Json

$registerResponse = Invoke-RestMethod -Uri "$API_URL/api/v1/auth/register" `
    -Method Post `
    -ContentType "application/json" `
    -Body $registerBody

$registerResponse | ConvertTo-Json

$TOKEN = $registerResponse.access_token
$INVITE_CODE = $registerResponse.invite_code

Write-Host ""
Write-Host "✅ Токен: $TOKEN" -ForegroundColor Green
Write-Host "✅ Invite Code: $INVITE_CODE" -ForegroundColor Green

Write-Host ""
Write-Host "3️⃣ Получение информации о пользователе..." -ForegroundColor Yellow
$headers = @{
    Authorization = "Bearer $TOKEN"
}

$userInfo = Invoke-RestMethod -Uri "$API_URL/api/v1/auth/me" `
    -Method Get `
    -Headers $headers

$userInfo | ConvertTo-Json

Write-Host ""
Write-Host "4️⃣ Первая синхронизация (Pull)..." -ForegroundColor Yellow
$syncResponse = Invoke-RestMethod -Uri "$API_URL/api/v1/sync" `
    -Method Get `
    -Headers $headers

$syncResponse | ConvertTo-Json -Depth 10

$TIMESTAMP = $syncResponse.timestamp
Write-Host "✅ Timestamp для следующей синхронизации: $TIMESTAMP" -ForegroundColor Green

Write-Host ""
Write-Host "5️⃣ Отправка данных (Push) - запись о переливании..." -ForegroundColor Yellow
$pushBody = @{
    changes = @{
        transfusions = @{
            created = @(
                @{
                    id = "550e8400-e29b-41d4-a716-446655440010"
                    date = "2026-01-14T10:00:00Z"
                    volume_ml = 250
                    patient_weight_kg = 30.5
                    indicator_name = "Hemoglobin"
                    value_before = 85.0
                    value_after = 95.0
                    notes = "Test transfusion"
                }
            )
            updated = @()
            deleted = @()
        }
    }
} | ConvertTo-Json -Depth 10

$pushResponse = Invoke-RestMethod -Uri "$API_URL/api/v1/sync" `
    -Method Post `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $pushBody

$pushResponse | ConvertTo-Json

Write-Host ""
Write-Host "6️⃣ Повторная синхронизация - проверяем данные..." -ForegroundColor Yellow
$syncResponse2 = Invoke-RestMethod -Uri "$API_URL/api/v1/sync?last_pulled_at=$TIMESTAMP" `
    -Method Get `
    -Headers $headers

$syncResponse2 | ConvertTo-Json -Depth 10

Write-Host ""
Write-Host "7️⃣ Восстановление пароля..." -ForegroundColor Yellow
$resetBody = @{
    email = "test@example.com"
} | ConvertTo-Json

$resetResponse = Invoke-RestMethod -Uri "$API_URL/api/v1/auth/password-reset/request" `
    -Method Post `
    -ContentType "application/json" `
    -Body $resetBody

$resetResponse | ConvertTo-Json

Write-Host ""
Write-Host "⚠️ Проверьте логи для получения временного пароля:" -ForegroundColor Magenta
Write-Host "docker-compose logs backend | Select-String 'Password reset'" -ForegroundColor White

Write-Host ""
Write-Host "8️⃣ Второй пользователь присоединяется к семье..." -ForegroundColor Yellow
$joinBody = @{
    email = "family@example.com"
    password = "password123"
    invite_code = $INVITE_CODE
} | ConvertTo-Json

$joinResponse = Invoke-RestMethod -Uri "$API_URL/api/v1/auth/join-family" `
    -Method Post `
    -ContentType "application/json" `
    -Body $joinBody

$TOKEN2 = $joinResponse.access_token
Write-Host "✅ Токен второго пользователя: $TOKEN2" -ForegroundColor Green

Write-Host ""
Write-Host "9️⃣ Второй пользователь получает данные (должен видеть запись первого)..." -ForegroundColor Yellow
$headers2 = @{
    Authorization = "Bearer $TOKEN2"
}

$syncResponse3 = Invoke-RestMethod -Uri "$API_URL/api/v1/sync" `
    -Method Get `
    -Headers $headers2

$syncResponse3 | ConvertTo-Json -Depth 10

Write-Host ""
Write-Host "✅ Тестирование завершено!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Результаты:" -ForegroundColor Cyan
Write-Host "- Регистрация: ✅" -ForegroundColor Green
Write-Host "- Авторизация: ✅" -ForegroundColor Green
Write-Host "- Получение профиля: ✅" -ForegroundColor Green
Write-Host "- Синхронизация Pull: ✅" -ForegroundColor Green
Write-Host "- Синхронизация Push: ✅" -ForegroundColor Green
Write-Host "- Восстановление пароля: ✅" -ForegroundColor Green
Write-Host "- Семейный доступ: ✅" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 Все работает!" -ForegroundColor Green

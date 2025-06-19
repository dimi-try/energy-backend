# Импортируем APIRouter из FastAPI для создания маршрутов
from fastapi import APIRouter, Depends, HTTPException, status, Request
# Импортируем функции для работы с авторизацией
from app.core.security import create_access_token, verify_token, validate
# import time
# Импортируем urllib.parse для обработки данных запроса
import urllib.parse

# Создаём маршрутизатор для эндпоинтов авторизации
router = APIRouter()

# Определяем эндпоинт для проверки авторизации
@router.post("/verify")
async def authorization_test(
    # Объект запроса
    request: Request
):
    # Извлекаем данные из тела запроса
    authorization_data = await request.json()
    # Парсим данные для получения hash и auth_date
    parsed_query = urllib.parse.parse_qs(authorization_data)
    # Получаем значение hash из данных
    hash_received = parsed_query.get('hash', [None])[0]
    # Получаем значение auth_date и преобразуем в int
    auth_date = int(parsed_query.get('auth_date', [0])[0])

    # Проверяем, предоставлен ли hash
    if not hash_received:
        # Вызываем исключение, если hash не предоставлен
        raise HTTPException(status_code=400, detail="Hash not provided")

    # Валидируем данные и проверяем актуальность hash
    if validate(hash_received, authorization_data):
        # Закомментированная проверка времени (сохранена как есть)
        # current_unix_time = int(time.time())
        # timeout_seconds = 3600  # Таймаут на верификацию (1 час)
        # if current_unix_time - auth_date > timeout_seconds:
        #     raise HTTPException(status_code=403, detail="Verification failed due to timeout")
        
        # Создаём JWT-токен для успешной верификации
        access_token = create_access_token({"sub": "user_id"}, expires_delta=3600)
        # Возвращаем успешный ответ с токеном
        return {"success": True, "message": "Verification successful", "access_token": access_token}
    else:
        # Вызываем исключение, если верификация не удалась
        raise HTTPException(status_code=403, detail="Verification failed")

# Защищенный эндпоинт, доступный только для авторизованных пользователей
@router.get("/protected")
async def protected_endpoint(
    # Зависимость: проверка токена
    token: str = Depends(verify_token)
):
    # Возвращаем сообщение и данные пользователя из токена
    return {"message": "Protected content", "user_data": token}
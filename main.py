import hmac
import hashlib
import time
import os
import urllib.parse
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

BOT_TOKEN = 'your-token'  # Получаем токен бота из переменных окружения

app = FastAPI()

# Включение CORS для всех источников
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Функция для валидации данных
def validate(hash_str, init_data):
    # Парсинг данных из строки
    parsed_query = urllib.parse.parse_qs(init_data)

    # Сортировка данных и создание строки для проверки хэша
    init_data = sorted([
        chunk.split("=")
        for chunk in urllib.parse.unquote(init_data).split("&")
        if not chunk.startswith("hash=")
    ], key=lambda x: x[0])

    init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])

    # Создание секретного ключа и вычисление хэша
    secret_key = hmac.new("WebAppData".encode(), BOT_TOKEN.encode(), hashlib.sha256).digest()
    data_check = hmac.new(secret_key, init_data.encode(), hashlib.sha256)

    # Сравнение вычисленного хэша с переданным
    return data_check.hexdigest() == hash_str

# Эндпоинт для авторизации
@app.post("/auth/verify")
async def authorization_test(request: Request):
    # print(request)
    # Получение данных из запроса
    authorization_data = await request.json()
    # print(authorization_data)
    # Парсинг данных для извлечения hash и auth_date
    parsed_query = urllib.parse.parse_qs(authorization_data)
    hash_received = parsed_query.get('hash', [None])[0]
    auth_date = int(parsed_query.get('auth_date', [0])[0])

    # Проверка наличия hash
    if not hash_received:
        raise HTTPException(status_code=400, detail="Hash not provided")

    # Валидация данных
    if validate(hash_received, authorization_data):
        current_unix_time = int(time.time())
        timeout_seconds = 3600
        if current_unix_time - auth_date > timeout_seconds:
            raise HTTPException(status_code=403, detail="Verification failed due to timeout")
        return {"success": True, "message": "Verification successful"}
    else:
        raise HTTPException(status_code=403, detail="Verification failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

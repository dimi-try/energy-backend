import hmac
import hashlib
import time
import os
from fastapi import HTTPException
from jose import jwt, JWTError
from dotenv import load_dotenv
import urllib.parse
from typing import Optional

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем секретный ключ, алгоритм шифрования и токен бота из переменных окружения
BACKEND_SECRET_KEY = os.getenv('BACKEND_SECRET_KEY')
BACKEND_ALGORITHM = os.getenv('BACKEND_ALGORITHM')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Функция для создания JWT-токена (токена доступа)
def create_access_token(data: dict, expires_delta: Optional[float] = None):
    # Копируем данные для кодирования в JWT
    to_encode = data.copy()
    # Устанавливаем срок действия токена (по умолчанию 1 час, если не передано время жизни токена)
    expire = time.time() + expires_delta if expires_delta else time.time() + 3600
    to_encode.update({"exp": expire})
    # Кодируем JWT с использованием секретного ключа и указанного алгоритма
    encoded_jwt = jwt.encode(to_encode, BACKEND_SECRET_KEY, algorithm=BACKEND_ALGORITHM)
    return encoded_jwt

# Функция для верификации JWT-токена
def verify_token(token: str):
    try:
        # Декодируем токен с использованием секретного ключа и алгоритма
        payload = jwt.decode(token, BACKEND_SECRET_KEY, algorithms=[BACKEND_ALGORITHM])
        return payload
    except JWTError:
        # Если произошла ошибка декодирования, возвращаем ошибку 401 (Unauthorized)
        raise HTTPException(status_code=401, detail="Invalid token")

# Функция для валидации данных, полученных от Telegram Web App
def validate(hash_str, init_data):
    # Разбираем и сортируем данные, исключая параметр hash
    parsed_query = urllib.parse.parse_qs(init_data)
    init_data = sorted([chunk.split("=") for chunk in urllib.parse.unquote(init_data).split("&") if not chunk.startswith("hash=")], key=lambda x: x[0])
    init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])

    # Генерируем секретный ключ для подписи данных на основе токена бота
    secret_key = hmac.new("WebAppData".encode(), BOT_TOKEN.encode(), hashlib.sha256).digest()
    # Создаем проверочную хэш-подпись данных
    data_check = hmac.new(secret_key, init_data.encode(), hashlib.sha256)

    # Возвращаем True, если хэш-подпись совпадает с переданным хэшем, иначе False
    return data_check.hexdigest() == hash_str

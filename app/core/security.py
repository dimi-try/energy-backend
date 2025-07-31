import hmac
import hashlib
import time
import os
from fastapi import HTTPException, Depends
from jose import jwt, JWTError
from dotenv import load_dotenv
from urllib.parse import parse_qs
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.users import get_user_role  # Импортируем для получения роли

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем секретный ключ, алгоритм и токен бота из переменных окружения
BACKEND_SECRET_KEY = os.getenv("BACKEND_SECRET_KEY")
BACKEND_ALGORITHM = os.getenv("BACKEND_ALGORITHM")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Проверяем наличие необходимых переменных окружения
if not all([BACKEND_SECRET_KEY, BACKEND_ALGORITHM, BOT_TOKEN]):
    raise ValueError("Не заданы необходимые переменные окружения (BOT_TOKEN, BACKEND_SECRET_KEY, BACKEND_ALGORITHM)")

# Функция для создания JWT-токена
def create_access_token(data: dict, expires_delta: float = 3600, db: Session = None):
    """
    Создает JWT-токен с данными пользователя, ролью и сроком действия.
    :param data: Данные для включения в токен (например, user_id)
    :param expires_delta: Время жизни токена в секундах (по умолчанию 1 час)
    :param db: Сессия базы данных для получения роли
    :return: JWT-токен
    """
    to_encode = data.copy()
    expire = time.time() + expires_delta
    to_encode.update({"exp": expire})
    if db and "sub" in to_encode:
        user_id = to_encode["sub"]
        role = get_user_role(db, int(user_id))
        to_encode.update({"role": role})
    encoded_jwt = jwt.encode(to_encode, BACKEND_SECRET_KEY, algorithm=BACKEND_ALGORITHM)
    return encoded_jwt

# Функция для верификации JWT-токена
def verify_token(token: str):
    """
    Проверяет валидность JWT-токена.
    :param token: JWT-токен
    :return: Данные из токена или исключение
    """
    try:
        # Декодируем токен с использованием секретного ключа и алгоритма
        payload = jwt.decode(token, BACKEND_SECRET_KEY, algorithms=[BACKEND_ALGORITHM])
        return payload
    except JWTError:
        # Если произошла ошибка декодирования, возвращаем ошибку 401 (Unauthorized)
        raise HTTPException(status_code=401, detail="Invalid token")

# Новая функция для проверки роли администратора
def verify_admin_token(token: str, db: Session = Depends(get_db)):
    """
    Проверяет, что токен принадлежит администратору.
    :param token: JWT-токен
    :param db: Сессия базы данных
    :return: Данные токена или исключение
    """
    payload = verify_token(token)
    user_id = payload.get("sub")
    role = payload.get("role")
    if not user_id or not role:
        raise HTTPException(status_code=401, detail="Invalid token: user_id or role not found")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized: admin role required")
    return payload

# Функция для валидации Telegram initData (полученных от Telegram Web App)
def validate_telegram_init_data(init_data: str) -> dict:
    """
    Проверяет подлинность initData от Telegram, возвращает данные пользователя.
    :param init_data: Строка initData от Telegram
    :return: Декодированные данные пользователя или исключение
    """
    # Парсим initData
    parsed_data = parse_qs(init_data)
    hash_received = parsed_data.get("hash", [None])[0]
    if not hash_received:
        raise HTTPException(status_code=400, detail="Hash не предоставлен")

    # Формируем data-check-string
    data_check_list = [
        f"{key}={value[0]}" for key, value in parsed_data.items() if key != "hash"
    ]
    data_check_list.sort()
    data_check_string = "\n".join(data_check_list)

    # Генерируем секретный ключ HMAC-SHA256 от BOT_TOKEN
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=BOT_TOKEN.encode(),
        digestmod=hashlib.sha256
    ).digest()

    # Вычисляем HMAC-SHA256 подпись
    computed_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    # Проверяем совпадение хэша
    if computed_hash != hash_received:
        raise HTTPException(status_code=403, detail="Недействительная подпись initData")

    # Проверяем актуальность данных (не старше 1 часа)
    auth_date = int(parsed_data.get("auth_date", [0])[0])
    current_time = int(time.time())
    if current_time - auth_date > 3600:
        raise HTTPException(status_code=403, detail="initData устарели")

    # Декодируем user из JSON
    import json
    user_data = json.loads(parsed_data.get("user", ["{}"])[0])
    return user_data
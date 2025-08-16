from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import hmac
import hashlib
import time
from jose import jwt, JWTError
from urllib.parse import parse_qs
import json

from app.core.config import BACKEND_SECRET_KEY, BACKEND_ALGORITHM, BOT_TOKEN

from app.db.database import get_db
from app.db.models import Role, UserRole

# Проверка наличия необходимых переменных окружения
if not all([BACKEND_SECRET_KEY, BACKEND_ALGORITHM, BOT_TOKEN]):
    # Выбрасываем исключение, если какая-либо переменная не задана
    raise ValueError("Не заданы необходимые переменные окружения (BOT_TOKEN, BACKEND_SECRET_KEY, BACKEND_ALGORITHM)")

# Настройка OAuth2 для проверки JWT-токена с указанием URL для получения токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/verify")

# Функция для получения текущего пользователя на основе JWT-токена
def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Проверяет JWT-токен и возвращает данные текущего пользователя.
    :param token: JWT-токен, полученный через OAuth2
    :return: Словарь с данными пользователя (user_id и роль)
    """
    # Верификация токена с помощью функции verify_token
    payload = verify_token(token)
    # Извлечение user_id из поля "sub" в токене
    user_id = payload.get("sub")
    # Проверка, что user_id присутствует в токене
    if not user_id:
        # Выбрасываем исключение, если user_id не найден
        raise HTTPException(status_code=401, detail="Invalid token: user_id not found")
    # Возвращаем словарь с user_id и ролью (по умолчанию "user", если роль не указана)
    return {"user_id": int(user_id), "role": payload.get("role", "user")}

# Функция для получения роли пользователя по его ID
def get_user_role(db: Session, user_id: int) -> str:
    """
    Получает роль пользователя по его ID из базы данных.
    :param db: Сессия базы данных
    :param user_id: ID пользователя
    :return: Название роли (например, "admin" или "user")
    """
    # Запрос к таблице UserRole для поиска роли пользователя по user_id
    user_role = db.query(UserRole).filter(UserRole.user_id == user_id).first()
    # Если роль не найдена, возвращаем "user" по умолчанию
    if not user_role:
        return "user"
    # Запрос к таблице Role для получения имени роли по role_id
    role = db.query(Role).filter(Role.id == user_role.role_id).first()
    # Возвращаем имя роли, если она найдена, иначе "user"
    return role.name if role else "user"

# Функция для создания JWT-токена
def create_access_token(data: dict, expires_delta: float = 3600, db: Session = None):
    """
    Создает JWT-токен с данными пользователя, ролью и сроком действия.
    :param data: Данные для включения в токен (например, user_id)
    :param expires_delta: Время жизни токена в секундах (по умолчанию 1 час)
    :param db: Сессия базы данных для получения роли
    :return: JWT-токен в виде строки
    """
    # Копируем входные данные, чтобы не изменять оригинальный словарь
    to_encode = data.copy()
    # Вычисляем время истечения токена (текущее время + expires_delta)
    expire = time.time() + expires_delta
    # Добавляем поле exp (время истечения) в данные токена
    to_encode.update({"exp": expire})
    # Если передана сессия базы данных и в данных есть user_id (sub)
    if db and "sub" in to_encode:
        # Извлекаем user_id из данных
        user_id = to_encode["sub"]
        # Получаем роль пользователя из базы данных
        role = get_user_role(db, int(user_id))
        # Добавляем роль в данные токена
        to_encode.update({"role": role})
    # Кодируем данные в JWT-токен с использованием секретного ключа и алгоритма
    encoded_jwt = jwt.encode(to_encode, BACKEND_SECRET_KEY, algorithm=BACKEND_ALGORITHM)
    # Возвращаем закодированный токен
    return encoded_jwt

# Функция для верификации JWT-токена
def verify_token(token: str):
    """
    Проверяет валидность JWT-токена.
    :param token: JWT-токен
    :return: Данные из токена или выбрасывает исключение
    """
    try:
        # Декодируем токен с использованием секретного ключа и алгоритма
        payload = jwt.decode(token, BACKEND_SECRET_KEY, algorithms=[BACKEND_ALGORITHM])
        # Возвращаем декодированные данные токена
        return payload
    except JWTError:
        # Если произошла ошибка декодирования, выбрасываем исключение 401
        raise HTTPException(status_code=401, detail="Invalid token")

# Функция для проверки токена администратора
def verify_admin_token(token: str, db: Session = Depends(get_db)):
    """
    Проверяет, что токен принадлежит администратору.
    :param token: JWT-токен
    :param db: Сессия базы данных
    :return: Данные токена или выбрасывает исключение
    """
    # Верифицируем токен
    payload = verify_token(token)
    # Извлекаем user_id из поля "sub"
    user_id = payload.get("sub")
    # Извлекаем роль из токена
    role = payload.get("role")
    # Проверяем, что user_id и роль присутствуют в токене
    if not user_id or not role:
        # Выбрасываем исключение, если user_id или роль не найдены
        raise HTTPException(status_code=401, detail="Invalid token: user_id or role not found")
    # Проверяем, что роль является "admin"
    if role != "admin":
        # Выбрасываем исключение 403, если роль не администраторская
        raise HTTPException(status_code=403, detail="Not authorized: admin role required")
    # Возвращаем данные токена
    return payload

# Функция для валидации Telegram initData
def validate_telegram_init_data(init_data: str) -> dict:
    """
    Проверяет подлинность initData от Telegram и возвращает данные пользователя.
    :param init_data: Строка initData от Telegram
    :return: Декодированные данные пользователя или выбрасывает исключение
    """
    # Парсим initData в словарь
    parsed_data = parse_qs(init_data)
    # Извлекаем хэш из initData
    hash_received = parsed_data.get("hash", [None])[0]
    # Проверяем, что хэш предоставлен
    if not hash_received:
        # Выбрасываем исключение, если хэш отсутствует
        raise HTTPException(status_code=400, detail="Hash не предоставлен")
    # Формируем data-check-string из всех параметров, кроме hash
    data_check_list = [
        f"{key}={value[0]}" for key, value in parsed_data.items() if key != "hash"
    ]
    # Сортируем параметры для корректной генерации подписи
    data_check_list.sort()
    # Объединяем параметры в строку, разделяя их переносами строки
    data_check_string = "\n".join(data_check_list)
    # Генерируем секретный ключ HMAC-SHA256 на основе BOT_TOKEN
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=BOT_TOKEN.encode(),
        digestmod=hashlib.sha256
    ).digest()
    # Вычисляем HMAC-SHA256 подпись для data-check-string
    computed_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    # Проверяем совпадение вычисленного хэша с полученным
    if computed_hash != hash_received:
        # Выбрасываем исключение, если подпись недействительна
        raise HTTPException(status_code=403, detail="Недействительная подпись initData")
    # Извлекаем время аутентификации из initData
    auth_date = int(parsed_data.get("auth_date", [0])[0])
    # Получаем текущее время
    current_time = int(time.time())
    # Проверяем, что данные не устарели (не старше 1 часа)
    if current_time - auth_date > 3600:
        # Выбрасываем исключение, если данные устарели
        raise HTTPException(status_code=403, detail="initData устарели")
    # Декодируем данные пользователя из JSON-строки
    user_data = json.loads(parsed_data.get("user", ["{}"])[0])
    # Возвращаем данные пользователя
    return user_data
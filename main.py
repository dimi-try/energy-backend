import hmac  # Импорт библиотеки для работы с HMAC
import hashlib  # Импорт библиотеки для работы с хэшированием
import time  # Импорт библиотеки для работы с временем
import os  # Импорт библиотеки для работы с операционной системой (для получения переменных окружения)
import urllib.parse  # Импорт библиотеки для работы с URL и строками запроса
from fastapi import FastAPI, HTTPException, Request, Depends  # Импорт FastAPI, HTTPException и Request для обработки запросов
from fastapi.middleware.cors import CORSMiddleware  # Импорт CORS middleware для управления CORS
from dotenv import load_dotenv  # Импорт функции для загрузки переменных окружения из .env файла
from pydantic import BaseModel  # Импорт BaseModel для валидации данных
from typing import Optional, List  # Импорт Optional и List для типов данных
from jose import JWTError, jwt  # Импорт JWT для генерации и проверки токенов
import asyncpg

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получаем токен бота и секрет для JWT из переменных окружения
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SECRET_KEY = os.getenv('SECRET_KEY')  # Секретный ключ для JWT
ALGORITHM = os.getenv('ALGORITHM')  # Алгоритм хэширования для JWT
DATABASE_URL = os.getenv('DATABASE_URL')  # URL базы данных PostgreSQL

# Создание экземпляра FastAPI приложения
app = FastAPI()

# Включение CORS для всех источников
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешение запросов с любых источников
    allow_credentials=True,  # Разрешение отправки кук и других учетных данных
    allow_methods=["*"],  # Разрешение всех методов HTTP (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешение всех заголовков HTTP
)

# Модели для сериализации данных
class BrandModel(BaseModel):
    id: int
    name: str

class EnergeticModel(BaseModel):
    id: int
    name: Optional[str]
    brand: BrandModel
    rating: float

# Функция для генерации JWT токена
def create_access_token(data: dict, expires_delta: Optional[float] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = time.time() + expires_delta
    else:
        expire = time.time() + 3600  # Срок действия токена 1 час
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Функция для проверки JWT токена
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Функция для валидации данных
def validate(hash_str, init_data):
    # Парсинг данных из строки (преобразование строки запроса в словарь)
    parsed_query = urllib.parse.parse_qs(init_data)

    # Сортировка данных и создание строки для проверки хэша
    init_data = sorted([
        chunk.split("=")  # Разделяем каждый элемент на ключ и значение
        for chunk in urllib.parse.unquote(init_data).split("&")  # Декодируем URL и разделяем на пары ключ-значение
        if not chunk.startswith("hash=")  # Пропускаем параметр "hash"
    ], key=lambda x: x[0])  # Сортируем по ключу

    # Создаем строку для проверки хэша
    init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])

    # Создание секретного ключа для вычисления хэша
    secret_key = hmac.new("WebAppData".encode(), BOT_TOKEN.encode(), hashlib.sha256).digest()
    
    # Вычисляем хэш для данных
    data_check = hmac.new(secret_key, init_data.encode(), hashlib.sha256)

    # Сравниваем вычисленный хэш с переданным
    return data_check.hexdigest() == hash_str

# Эндпоинт для авторизации и генерации токена
@app.post("/auth/verify")
async def authorization_test(request: Request):
    # Получение данных из запроса
    authorization_data = await request.json()
    
    # Парсинг данных для извлечения hash и auth_date
    parsed_query = urllib.parse.parse_qs(authorization_data)
    hash_received = parsed_query.get('hash', [None])[0]  # Получаем значение hash из запроса
    auth_date = int(parsed_query.get('auth_date', [0])[0])  # Получаем значение auth_date из запроса

    # Проверка наличия hash
    if not hash_received:
        raise HTTPException(status_code=400, detail="Hash not provided")

    # Валидация данных
    if validate(hash_received, authorization_data):
        current_unix_time = int(time.time())  # Получаем текущее время в формате UNIX
        timeout_seconds = 3600  # Устанавливаем время жизни данных (1 час)
        if current_unix_time - auth_date > timeout_seconds:
            raise HTTPException(status_code=403, detail="Verification failed due to timeout")
        
        # Генерация и возвращение JWT токена
        access_token = create_access_token({"sub": "user_id"}, expires_delta=3600)  # Пример данных payload
        return {"success": True, "message": "Verification successful", "access_token": access_token}
    else:
        raise HTTPException(status_code=403, detail="Verification failed")

# Эндпоинт для проверки токена
@app.get("/auth/protected")
async def protected_endpoint(token: str = Depends(verify_token)):
    return {"message": "Protected content", "user_data": token}

# Эндпоинт для получения списка энергетиков с брендами и рейтингами
@app.get("/api/energetics", response_model=List[EnergeticModel])
async def get_energetics():
    query = """
    SELECT 
        e.id AS energy_id, 
        e.name AS energy_name, 
        b.id AS brand_id, 
        b.name AS brand_name, 
        COALESCE(AVG(r.rating), 0) AS average_rating
    FROM 
        Energetics e
    JOIN 
        Brands b ON e.brand_id = b.id
    LEFT JOIN 
        Ratings r ON e.id = r.energy_id
    GROUP BY 
        e.id, b.id
    LIMIT 5;
    """
    
    try:
        conn = await app.state.db_pool.acquire()  # Получаем соединение из пула
        rows = await conn.fetch(query)
        await app.state.db_pool.release(conn)  # Возвращаем соединение в пул

        energetics = []
        for row in rows:
            energetics.append({
                "id": row["energy_id"],
                "name": row["energy_name"],
                "brand": {
                    "id": row["brand_id"],
                    "name": row["brand_name"]
                },
                "rating": float(row["average_rating"])
            })

        return energetics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Создаем пул соединений при запуске приложения
@app.on_event("startup")
async def startup():
    app.state.db_pool = await asyncpg.create_pool(DATABASE_URL)

# Закрываем пул соединений при остановке приложения
@app.on_event("shutdown")
async def shutdown():
    await app.state.db_pool.close()

# Запуск сервера
if __name__ == "__main__":
    import uvicorn  # Импорт uvicorn для запуска сервера
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)  # Запуск приложения на локальном сервере

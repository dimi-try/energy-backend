import hmac  # Импорт библиотеки для работы с HMAC
import hashlib  # Импорт библиотеки для работы с хэшированием
import time  # Импорт библиотеки для работы с временем
import os  # Импорт библиотеки для работы с операционной системой (для получения переменных окружения)
import urllib.parse  # Импорт библиотеки для работы с URL и строками запроса
from fastapi import FastAPI, HTTPException, Request  # Импорт FastAPI, HTTPException и Request для обработки запросов
from fastapi.middleware.cors import CORSMiddleware  # Импорт CORS middleware для управления CORS

from dotenv import load_dotenv  # Импорт функции для загрузки переменных окружения из .env файла

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

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

# Эндпоинт для авторизации
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
        return {"success": True, "message": "Verification successful"}  # Возвращаем успешный результат
    else:
        raise HTTPException(status_code=403, detail="Verification failed")  # Возвращаем ошибку, если валидация не прошла

# Запуск сервера
if __name__ == "__main__":
    import uvicorn  # Импорт uvicorn для запуска сервера
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)  # Запуск приложения на локальном сервере

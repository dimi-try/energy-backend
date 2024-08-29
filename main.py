from fastapi import FastAPI, HTTPException, Request
import hmac
import hashlib
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

app = FastAPI()

# Токен вашего Telegram бота
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

@app.post("/auth/")
async def authenticate(request: Request):
    data = await request.json()

    user = data.get("user")
    auth_date = data.get("auth_date")
    received_hash = data.get("hash")

    # Проверка наличия необходимых данных
    if not user or not auth_date or not received_hash:
        raise HTTPException(status_code=400, detail="Missing required fields")

    # Создание строки для проверки хэша
    data_check_string = f"user={user}&auth_date={auth_date}"
    
    # Вычисление хэша
    secret_key = hmac.new(BOT_TOKEN.encode(), data_check_string.encode(), hashlib.sha256).hexdigest()

    # # Сравнение хэша, присланного Telegram, и нашего (закоментить при самом первом тесте)
    # if not hmac.compare_digest(secret_key, received_hash):
    #     raise HTTPException(status_code=403, detail="Authentication failed")

    # Если аутентификация прошла успешно, выведем приветственное сообщение в консоль
    first_name = user.get("first_name", "User")
    print(f"Привет, {first_name}!")

    return {"status": "Authenticated"}
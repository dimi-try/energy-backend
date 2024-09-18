from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import api_router  # Импорт маршрутов
from app.database import create_db, close_db  # Импорт функций для работы с базой данных
import sys
import os

# Добавляем путь к текущему файлу в системный путь (sys.path), чтобы модуль мог находить другие файлы проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Инициализация экземпляра FastAPI
app = FastAPI()

# Настройка CORS (Cross-Origin Resource Sharing) для управления запросами из других доменов
# Этот middleware позволяет запросы с любых источников ("*") и позволяет использовать куки и заголовки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить запросы с любых источников (можно ограничить список доменов)
    allow_credentials=True,  # Разрешить отправку куки
    allow_methods=["*"],  # Разрешить любые HTTP методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешить любые заголовки
)

# Подключение роутеров к приложению
app.include_router(api_router)

# Обработчик события старта приложения
@app.on_event("startup")
async def startup_event():
    # Функция для инициализации базы данных при запуске приложения
    await create_db()

# Обработчик события завершения работы приложения
@app.on_event("shutdown")
async def shutdown_event():
    # Функция для закрытия подключения к базе данных при остановке приложения
    await close_db()

# Основная точка входа в приложение, запуск через uvicorn
if __name__ == "__main__":
    import uvicorn
    # Запуск приложения с указанием адреса (localhost) и порта (8000), с автообновлением кода (reload=True)
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

# Импортируем FastAPI для создания приложения
from fastapi import FastAPI
# Импортируем CORS middleware для разрешения кросс-доменных запросов
from fastapi.middleware.cors import CORSMiddleware
# Импортируем маршруты версии v1
from app.api.v1.router import api_router
# Импортируем StaticFiles для обслуживания статических файлов
from fastapi.staticfiles import StaticFiles

from app.core.config import FRONTEND_URL, UPLOAD_DIR_ENERGY, UPLOAD_DIR_REVIEW

# Создаём экземпляр приложения FastAPI
app = FastAPI(
    # Устанавливаем заголовок приложения
    title="Energy Drinks API",
    # Устанавливаем описание приложения
    description="API for managing energy drinks, brands, reviews, and user profiles",
    # Устанавливаем версию API
    version="1.0.0"
)

# Определяем список разрешённых источников для CORS
origins = [
    FRONTEND_URL
]

# Добавляем CORS middleware для обработки кросс-доменных запросов
app.add_middleware(
    # Указываем класс middleware
    CORSMiddleware,
    # Разрешаем указанные источники
    allow_origins=origins,
    # Разрешаем отправку куки и заголовков авторизации
    allow_credentials=True,
    # Разрешаем все HTTP-методы
    allow_methods=["*"],
    # Разрешаем все заголовки
    allow_headers=["*"],
)

# Подключаем директории для статических файлов (изображения)
app.mount("/uploads/energy", StaticFiles(directory=UPLOAD_DIR_ENERGY), name="energy_uploads")
app.mount("/uploads/reviews", StaticFiles(directory=UPLOAD_DIR_REVIEW), name="review_uploads")

# Подключаем маршруты версии v1 с префиксом /api/v1
app.include_router(
    # Указываем маршрутизатор
    api_router,
    # Устанавливаем префикс для маршрутов
    prefix="/api/v1"
)

# Определяем корневой эндпоинт для проверки работы API
@app.get("/")
async def root():
    # Возвращаем приветственное сообщение
    return {"message": "Welcome to the Energy Drinks API"}
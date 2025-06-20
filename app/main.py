# Импортируем FastAPI для создания приложения
from fastapi import FastAPI
# Импортируем CORS middleware для разрешения кросс-доменных запросов
from fastapi.middleware.cors import CORSMiddleware
# Импортируем маршруты версии v1
from app.api.v1.router import api_router

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
    # Разрешаем запросы с фронтенда (локальный хост)
    "http://localhost:3000",
    # Разрешаем запросы с продакшн-фронтенда (замените на ваш домен)
    "https://your-frontend-domain.com",
]
origins = ["*"]  # Разрешаем все источники (для разработки)

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
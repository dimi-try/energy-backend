# Импортируем APIRouter из FastAPI для создания маршрутизатора
from fastapi import APIRouter
# Импортируем маршруты для брендов
from app.api.v1.endpoints import brands
# Импортируем маршруты для энергетиков
from app.api.v1.endpoints import energies
# Импортируем маршруты для пользователей
from app.api.v1.endpoints import users
# Импортируем маршруты для оценок
from app.api.v1.endpoints import ratings
# Импортируем маршруты для отзывов
from app.api.v1.endpoints import reviews
# Импортируем маршруты для критериев
from app.api.v1.endpoints import criteria
# Импортируем маршруты для категорий
from app.api.v1.endpoints import categories
# Импортируем маршруты для топов
from app.api.v1.endpoints import top
# Импортируем маршруты для авторизации
from app.api.v1.endpoints import auth

# Создаём маршрутизатор для версии v1
api_router = APIRouter()

# Подключаем маршруты для брендов с тегом "brands"
api_router.include_router(
    # Указываем маршрутизатор брендов
    brands.router,
    # Устанавливаем префикс для маршрутов
    prefix="/brands",
    # Устанавливаем тег для документации
    tags=["brands"]
)

# Подключаем маршруты для энергетиков с тегом "energies"
api_router.include_router(
    # Указываем маршрутизатор энергетиков
    energies.router,
    # Устанавливаем префикс для маршрутов
    prefix="/energies",
    # Устанавливаем тег для документации
    tags=["energies"]
)

# Подключаем маршруты для пользователей с тегом "users"
api_router.include_router(
    # Указываем маршрутизатор пользователей
    users.router,
    # Устанавливаем префикс для маршрутов
    prefix="/users",
    # Устанавливаем тег для документации
    tags=["users"]
)

# Подключаем маршруты для оценок с тегом "ratings"
api_router.include_router(
    # Указываем маршрутизатор оценок
    ratings.router,
    # Устанавливаем префикс для маршрутов
    prefix="/ratings",
    # Устанавливаем тег для документации
    tags=["ratings"]
)

# Подключаем маршруты для отзывов с тегом "reviews"
api_router.include_router(
    # Указываем маршрутизатор отзывов
    reviews.router,
    # Устанавливаем префикс для маршрутов
    prefix="/reviews",
    # Устанавливаем тег для документации
    tags=["reviews"]
)

# Подключаем маршруты для критериев с тегом "criteria"
api_router.include_router(
    # Указываем маршрутизатор критериев
    criteria.router,
    # Устанавливаем префикс для маршрутов
    prefix="/criteria",
    # Устанавливаем тег для документации
    tags=["criteria"]
)

# Подключаем маршруты для категорий с тегом "categories"
api_router.include_router(
    # Указываем маршрутизатор категорий
    categories.router,
    # Устанавливаем префикс для маршрутов
    prefix="/categories",
    # Устанавливаем тег для документации
    tags=["categories"]
)

# Подключаем маршруты для топов с тегом "top"
api_router.include_router(
    # Указываем маршрутизатор топов
    top.router,
    # Устанавливаем префикс для маршрутов
    prefix="/top",
    # Устанавливаем тег для документации
    tags=["top"]
)

# Подключаем маршруты для авторизации с тегом "auth"
api_router.include_router(
    # Указываем маршрутизатор авторизации
    auth.router,
    # Устанавливаем префикс для маршрутов
    prefix="/auth",
    # Устанавливаем тег для документации
    tags=["auth"]
)
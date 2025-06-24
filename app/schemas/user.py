# Импортируем BaseModel из Pydantic для создания схем
from pydantic import BaseModel, EmailStr, Field, condecimal
# Импортируем Optional и List для аннотации
from typing import Optional, List
# Импортируем datetime для работы с датами
from datetime import datetime
# Импортируем схемы для брендов и энергетиков
from app.schemas.brand import Brand
from app.schemas.energy import Energy
# Импортируем базовую модель для отзывов
from app.schemas.review import ReviewBase

# =============== ПОЛЬЗОВАТЕЛИ ===============
# Определяем раздел для моделей, связанных с пользователями

# Базовая модель для пользователей, содержит общие поля
class UserBase(BaseModel):
    # Поле username: имя пользователя, обязательное, с максимальной длиной 100 символов
    username: str = Field(..., max_length=100)
    # Поле email: email пользователя, обязательное, с максимальной длиной 255 символов
    email: str = Field(..., max_length=255)

# Модель для создания пользователя, наследуется от UserBase
class UserCreate(UserBase):
    # Поле password: пароль пользователя, обязательное, длина от 8 до 255 символов
    password: str = Field(..., min_length=8, max_length=255)

# Полная модель пользователя, используется для возврата данных о пользователе
class User(UserBase):
    # Поле id: уникальный идентификатор пользователя
    id: int
    # Поле is_premium: флаг, указывающий, является ли пользователь премиум-пользователем
    is_premium: bool
    # Поле created_at: дата и время создания пользователя
    created_at: datetime
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True

"""
Сноска для User:
Эта модель используется в эндпоинте GET /users/{user_id}, который возвращает данные
о конкретном пользователе. Эндпоинт доступен только администраторам или самому пользователю.
"""

# =============== ПРОФИЛЬ ===============
# Определяем раздел для модели профиля пользователя

# Модель профиля пользователя, содержит статистику и данные пользователя
class UserProfile(BaseModel):
    # Поле user: объект пользователя
    user: User
    # Поле total_ratings: общее количество оценок пользователя
    total_ratings: int
    # Поле average_rating: средний рейтинг пользователя, от 0 до 10, необязательное
    average_rating: Optional[condecimal(ge=0, le=10, decimal_places=4)] = None
    # Поле favorite_brand: любимый бренд пользователя, необязательное
    favorite_brand: Optional[Brand] = None
    # Поле favorite_energy: любимый энергетик пользователя, необязательное
    favorite_energy: Optional[Energy] = None
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True

"""
Сноска для UserProfile:
Эта модель используется в эндпоинте GET /users/{user_id}/profile, который возвращает
профиль пользователя. Доступен только самому пользователю или администраторам.
"""

# =============== ОТЗЫВЫ ===============
# Определяем раздел для модели отзывов пользователя
class UserReviews(BaseModel):
    # Поле reviews: список отзывов пользователя
    reviews: List[ReviewBase]  # Здесь предполагается, что ReviewBase содержит информацию об отзыве
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True

"""
Сноска для UserReviews:
Эта модель используется в эндпоинте GET /users/{user_id}/reviews, который возвращает
список отзывов пользователя. Доступен только самому пользователю или администраторам.
"""
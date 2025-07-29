# Импортируем BaseModel из Pydantic для создания схем
from pydantic import BaseModel, condecimal
# Импортируем Optional и List для аннотации
from typing import Optional, List
# Импортируем datetime для работы с датами
from datetime import datetime
# Импортируем базовую модель для отзывов
from app.schemas.ratings import Rating, RatingBase

# Базовая модель для отзывов, содержит общие поля
class ReviewBase(BaseModel):
    # Поле energy_id: идентификатор энергетика, к которому относится отзыв
    energy_id: int
    # Поле user_id: идентификатор пользователя, оставившего отзыв
    user_id: int
    # Поле review_text: текст отзыва, обязательное
    review_text: str
    # Поле created_at: дата и время создания отзыва
    created_at: datetime
    # Поле ratings: список объектов оценок, связанных с отзывом
    ratings: List[Rating]

# Модель для отзывов пользователя, содержит информацию об энергетике и бренде
class ReviewsUser(ReviewBase):
    # Поле id: информация о id отзыва
    id: int
    # Поле energy: информация об энергетике
    energy: Optional[str] = None
    # Поле brand: информация о бренде (через энергетик)
    brand: Optional[str] = None  # Добавляем название бренда
    # Поле average_rating_review: средний рейтинг отзыва, значение оценки, от 0 до 10 с 4 знаками после запятой
    average_rating_review: condecimal(ge=0, le=10, decimal_places=4)
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True
        
# Импортируем схемы для пользователей
from app.schemas.users import UserBase

# Модель для создания отзыва, наследуется от ReviewBase
class ReviewCreate(ReviewBase):
    # Поле ratings: список оценок по критериям, связанных с отзывом
    ratings: List[RatingBase]

# Модель для обновления отзыва
class ReviewUpdate(BaseModel):
    # Поле review_text: текст отзыва, необязательное
    review_text: Optional[str] = None
    # Поле ratings: список оценок по критериям, необязательное
    ratings: Optional[List[RatingBase]] = None

# Полная модель отзыва, используется для возврата данных об отзыве
class Review(ReviewBase):
    # Поле id: уникальный идентификатор отзыва
    id: int
    # Информация о пользователе (его имя)
    user: UserBase
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True

# Модель для отзывов с рейтингами, используется для возврата данных об отзыве с рейтингами
class ReviewWithRatings(Review):
    # Поле average_rating_review: средний рейтинг отзыва, значение оценки, от 0 до 10 с 4 знаками после запятой
    average_rating_review: condecimal(ge=0, le=10, decimal_places=4)
# Импортируем BaseModel из Pydantic для создания схем
from pydantic import BaseModel
# Импортируем Optional и List для аннотации
from typing import Optional, List
# Импортируем datetime для работы с датами
from datetime import datetime
# Импортируем базовую модель для отзывов
from app.schemas.rating import Rating, RatingBase

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
    # Поле energy: информация об энергетике
    energy: Optional[str] = None
    # Поле brand: информация о бренде (через энергетика)
    brand: Optional[str] = None  # Добавляем название бренда
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True
        
# Импортируем схемы для пользователей
from app.schemas.user import UserBase

# Модель для создания отзыва, наследуется от ReviewBase
class ReviewCreate(ReviewBase):
    # Поле ratings: список оценок по критериям, связанных с отзывом
    ratings: List[RatingBase]

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


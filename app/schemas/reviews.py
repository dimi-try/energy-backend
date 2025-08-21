from pydantic import BaseModel, condecimal
from typing import Optional, List

from app.schemas.base import UserBase, ReviewBase, RatingBase

# =============== CREATE ===============
class ReviewCreate(ReviewBase):
    # список оценок по критериям, связанных с отзывом
    ratings: List[RatingBase]

# =============== READ ONE ===============
class Review(ReviewBase):
    # уникальный идентификатор отзыва
    id: int
    # Информация о пользователе (его имя)
    user: UserBase
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True

# =============== READ ALL REVIEWS ONE USER ===============
class ReviewsUser(ReviewBase):
    # информация о id отзыва
    id: int
    # информация об энергетике
    energy: Optional[str] = None
    # информация о бренде (через энергетик)
    brand: Optional[str] = None  # Добавляем название бренда
    # средний рейтинг отзыва, значение оценки, от 0 до 10 с 4 знаками после запятой
    average_rating_review: condecimal(ge=0, le=10, decimal_places=4)
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True

# =============== UPDATE ===============
class ReviewUpdate(BaseModel):
    # текст отзыва, необязательное
    review_text: Optional[str] = None
    # список оценок по критериям, необязательное
    ratings: Optional[List[RatingBase]] = None
    # URL изображения отзыва, необязательное
    image_url: Optional[str] = None

# =============== ONLY ADMINS ===============

# =============== READ ALL RATINGS ONE REVIEW ===============
class ReviewWithRatings(Review):
    # Поле average_rating_review: средний рейтинг отзыва, значение оценки, от 0 до 10 с 4 знаками после запятой
    average_rating_review: condecimal(ge=0, le=10, decimal_places=4)


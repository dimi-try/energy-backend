from pydantic import BaseModel, condecimal
from typing import Optional
from datetime import datetime

from app.schemas.base import RatingBase

# =============== READ ONE ===============
class Rating(RatingBase):
    # уникальный идентификатор оценки
    id: int
    # идентификатор отзыва, к которому относится оценка
    review_id: int
    # дата и время создания оценки
    created_at: datetime
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True
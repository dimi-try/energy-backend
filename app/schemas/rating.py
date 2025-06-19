# Импортируем BaseModel из Pydantic для создания схем
from pydantic import BaseModel, condecimal
# Импортируем Optional для аннотации
from typing import Optional
# Импортируем datetime для работы с датами
from datetime import datetime

# Определяем базовую схему для оценки
# Базовая модель для оценок, содержит общие поля
class RatingBase(BaseModel):
    # Поле criteria_id: идентификатор критерия, по которому ставится оценка
    criteria_id: int
    # Поле rating_value: значение оценки, от 0 до 10 с 4 знаками после запятой
    rating_value: condecimal(ge=0, le=10, decimal_places=4)
# Полная модель оценки, используется для возврата данных об оценке
class Rating(RatingBase):
    # Поле id: уникальный идентификатор оценки
    id: int
    # Поле review_id: идентификатор отзыва, к которому относится оценка
    review_id: int
    # Поле created_at: дата и время создания оценки
    created_at: datetime
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True
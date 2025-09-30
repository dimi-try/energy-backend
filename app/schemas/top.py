from pydantic import BaseModel, condecimal
from typing import Optional

from app.schemas.brands import Brand
from app.schemas.categories import Category

# =============== READ ENERGY CHART ===============
class EnergyTop(BaseModel):
    # уникальный идентификатор энергетика
    id: int
    # название энергетика
    name: str
    # средний рейтинг энергетика, от 0 до 10 с 4 знаками после запятой
    average_rating: condecimal(ge=0, le=10, decimal_places=4)
    # объект бренда энергетика
    brand: Brand
    # объект категории, необязательное
    category: Optional[Category] = None
    # URL изображения энергетика, необязательное
    image_url: Optional[str] = None
    # общее количество отзывов на энергетик
    review_count: int
    # Абсолютная позиция в топе без фильтров
    absolute_rank: int
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True

# =============== READ BRAND CHART ===============
class BrandTop(BaseModel):
    # уникальный идентификатор бренда
    id: int
    # название бренда
    name: str
    # средний рейтинг бренда, от 0 до 10 с 4 знаками после запятой
    average_rating: condecimal(ge=0, le=10, decimal_places=4)
    # количество энергетиков бренда, необязательное
    energy_count: Optional[int] = None
    # количество отзывов на энергетики бренда, необязательное
    review_count: Optional[int] = None
    # количество оценок на энергетики бренда, необязательное
    rating_count: Optional[int] = None
    # Абсолютная позиция в топе без фильтров
    absolute_rank: int
    class Config:
        from_attributes = True
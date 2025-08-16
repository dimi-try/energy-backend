from pydantic import BaseModel, Field
from typing import Optional, List
from app.schemas.base import BrandBase

# =============== READ ONE ===============
class Brand(BrandBase):
    # уникальный идентификатор бренда
    id: int
    # средний рейтинг бренда, необязательное, по умолчанию None
    average_rating: Optional[float] = None
    # количество энергетиков бренда, необязательное, по умолчанию None
    energy_count: Optional[int] = None
    # количество отзывов на энергетики бренда, необязательное
    review_count: Optional[int] = None
    # количество оценок на энергетики бренда, необязательное
    rating_count: Optional[int] = None
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True

# =============== READ ALL ENERGIES ONE BRAND===============
class BrandAndEnergies(BrandBase):
    # уникальный идентификатор бренда
    id: int
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True

# =============== ONLY ADMINS ===============

# =============== CREATE ===============
class BrandCreate(BrandBase):
    # Наследуем все поля из BrandBase без изменений, используется для POST-запросов
    pass

# =============== UPDATE ===============
class BrandUpdate(BrandBase):
    # Наследуем все поля из BrandBase, используется для PUT-запросов
    pass
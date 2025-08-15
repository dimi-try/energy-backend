from pydantic import BaseModel, Field
from typing import Optional, List

from app.schemas.brands import Brand, BrandAndEnergies
from app.schemas.categories import Category

from app.schemas.base import EnergyBase

# =============== READ ONE ===============
class Energy(EnergyBase):
    # уникальный идентификатор энергетика
    id: int
    # объект бренда, к которому относится энергетик
    brand: Brand
    # объект категории, необязательное, может быть None
    category: Optional[Category]
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True

# =============== READ ALL ENERGIES ONE BRAND===============
class EnergiesByBrand(EnergyBase):
    # уникальный идентификатор энергетика
    id: int
    # объект бренда без статистики, используется в списке энергетиков бренда
    brand: BrandAndEnergies
    # объект категории, необязательное
    category: Optional[Category]
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True

# =============== ONLY ADMINS ===============

# =============== CREATE ===============
class EnergyCreate(EnergyBase):
    # Наследуем все поля из EnergyBase без изменений, используется для POST-запросов
    pass

# =============== UPDATE ===============
class EnergyUpdate(EnergyBase):
    # Все поля необязательные для обновления
    name: Optional[str] = None
    brand_id: Optional[int] = None
    category_id: Optional[int] = None
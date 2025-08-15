from pydantic import BaseModel, Field
from typing import Optional, List

from app.schemas.base import CategoryBase

# =============== READ ONE ===============
class Category(CategoryBase):
    # уникальный идентификатор категории
    id: int
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True

# =============== ONLY ADMINS ===============

# =============== CREATE ===============
class CategoryCreate(CategoryBase):
    # Наследуем все поля из CategoryBase без изменений, используется для POST-запросов
    pass

# =============== UPDATE ===============
class CategoryUpdate(CategoryBase):
    # необязательное для обновления
    name: Optional[str] = None
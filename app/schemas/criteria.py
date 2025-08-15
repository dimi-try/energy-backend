from pydantic import BaseModel, Field
from typing import Optional, List

from app.schemas.base import CriteriaBase

# =============== READ ONE ===============
class Criteria(CriteriaBase):
    # уникальный идентификатор критерия
    id: int
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True

# =============== ONLY ADMINS ===============

# =============== UPDATE ===============
class CriteriaUpdate(CriteriaBase):
    # необязательное для обновления
    name: Optional[str] = None
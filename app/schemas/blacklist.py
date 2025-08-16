from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.base import BlacklistBase

# =============== ONLY ADMINS ===============

# =============== CREATE ===============
class BlacklistCreate(BlacklistBase):
    # такая же как и базовая
    pass

# =============== READ ONE ===============
class Blacklist(BlacklistBase):
    id: int
    # когда создан
    created_at: datetime
    # Имя пользователя для отображения
    username: Optional[str] = None

    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True
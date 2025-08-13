from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BlacklistBase(BaseModel):
    user_id: int
    reason: Optional[str] = None

class BlacklistCreate(BlacklistBase):
    pass

class Blacklist(BlacklistBase):
    id: int
    created_at: datetime
    username: Optional[str] = None  # Имя пользователя для отображения

    class Config:
        from_attributes = True
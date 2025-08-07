from pydantic import BaseModel, Field
from typing import Optional

# Базовая модель для пользователей, содержит общие поля
class UserBase(BaseModel):
    # Поле username: имя пользователя, обязательное, с максимальной длиной 100 символов
    username: str = Field(..., max_length=100)
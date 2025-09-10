from pydantic import BaseModel, Field, condecimal
from typing import Optional, List

from app.schemas.brands import Brand
from app.schemas.energies import Energy
from app.schemas.base import UserBase
from app.schemas.reviews import ReviewsUser

# =============== CREATE ===============
class UserCreate(UserBase):
    pass

# =============== READ ONE ===============
class User(UserBase):
    # уникальный идентификатор пользователя
    id: int
    # флаг, указывающий, является ли пользователь премиум-пользователем
    is_premium: bool
    # дата и время создания пользователя (в формате Unix timestamp)
    created_at: int
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True

# =============== UPDATE ===============
class UserUpdate(BaseModel):
    # имя пользователя, необязательное, с максимальной длиной 100 символов
    username: Optional[str] = Field(None, max_length=100)
    # URL изображения, необязательное
    image_url: Optional[str] = None
    
# =============== READ ONE PROFILE ===============
class UserProfile(BaseModel):
    # объект пользователя
    user: User
    # общее количество оценок пользователя
    total_ratings: int
    # средний рейтинг пользователя, от 0 до 10, необязательное
    average_rating: Optional[condecimal(ge=0, le=10, decimal_places=4)] = None
    # любимый бренд пользователя, необязательное
    favorite_brand: Optional[Brand] = None
    # любимый энергетик пользователя, необязательное
    favorite_energy: Optional[Energy] = None
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True

# =============== READ ALL REVIEWS ONE USER===============
class UserReviews(BaseModel):
    # список отзывов пользователя
    reviews: List[ReviewsUser]  # ReviewsUser содержит информацию об отзыве
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True
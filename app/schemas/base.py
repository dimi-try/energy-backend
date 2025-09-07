from pydantic import BaseModel, Field, condecimal
from typing import Optional, List
from datetime import datetime

# Базовая модель для оценок, содержит общие поля
class RatingBase(BaseModel):
    # идентификатор критерия, по которому ставится оценка
    criteria_id: int
    # значение оценки, от 0 до 10 с 4 знаками после запятой
    rating_value: condecimal(ge=0, le=10, decimal_places=4)
    
from app.schemas.ratings import Rating
# Базовая модель для отзывов, содержит общие поля
class ReviewBase(BaseModel):
    # идентификатор энергетика, к которому относится отзыв
    energy_id: int
    # идентификатор пользователя, оставившего отзыв
    user_id: int
    # текст отзыва, обязательное
    review_text: Optional[str] = None
    # URL изображения отзыва, необязательное
    image_url: Optional[str] = None
    # дата и время создания отзыва
    created_at: datetime
    # список объектов оценок, связанных с отзывом
    ratings: List[Rating]

# Базовая модель для критериев, содержит общие поля
class CriteriaBase(BaseModel):
    # название критерия, обязательное, с максимальной длиной 100 символов
    name: str = Field(..., max_length=100)
    
# Базовая модель для категорий, содержит общие поля
class CategoryBase(BaseModel):
    # название категории, обязательное, с максимальной длиной 100 символов
    name: str = Field(..., max_length=100)

# Базовая модель для энергетиков, содержит общие поля
class EnergyBase(BaseModel):
    # название энергетика, обязательное, с максимальной длиной 255 символов
    name: str = Field(..., max_length=255)
    # идентификатор бренда, к которому относится энергетик, обязательное
    brand_id: int
    # идентификатор категории, необязательное, по умолчанию None
    category_id: Optional[int] = None
    # описание энергетика, необязательное, строка
    description: Optional[str] = None
    # ингредиенты энергетика, необязательное, строка
    ingredients: Optional[str] = None
    # URL изображения энергетика, необязательное
    image_url: Optional[str] = None
    # средний рейтинг энергетика, необязательное
    average_rating: Optional[float] = None
    # количество отзывов на энергетик, необязательное
    review_count: Optional[int] = None
    
# Базовая модель для брендов, содержит общие поля
class BrandBase(BaseModel):
    # Поле name: название бренда, обязательное, с максимальной длиной 255 символов
    # Используется Field для валидации длины и указания, что поле обязательно (...)
    name: str = Field(..., max_length=255)

# Базовая схема для пользователей
class UserBase(BaseModel):
    # Поле username: имя пользователя, обязательное, с максимальной длиной 100 символов
    username: str = Field(..., max_length=100)
    # URL изображения, необязательное
    image_url: Optional[str] = None

# Базовая схема для черного списка
class BlacklistBase(BaseModel):
    # id польвателя
    user_id: int
    # причина добавления в черный список (необязательна)
    reason: Optional[str] = None
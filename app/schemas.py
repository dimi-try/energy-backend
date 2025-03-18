from pydantic import BaseModel, Field, condecimal
from typing import Optional, List
from datetime import datetime

# =============== БРЕНДЫ ===============
class BrandBase(BaseModel):
    name: str = Field(..., max_length=255)

class BrandCreate(BrandBase):
    pass

class Brand(BrandBase):
    id: int
    average_rating: Optional[float] = None
    energy_count: Optional[int] = None
    review_count: Optional[int] = None
    rating_count: Optional[int] = None
    class Config:
        from_attributes = True

# эта модель без статистики брендов специально для 
# списка всех энов принадлежащих определенному бренду
# /brands/{brand_id}/energies/
class BrandAndEnergies(BrandBase):
    id: int
    class Config:
        from_attributes = True

# =============== КАТЕГОРИИ ===============
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    class Config:
        from_attributes = True

# =============== ЭНЕРГЕТИКИ ===============
class EnergyBase(BaseModel):
    name: str = Field(..., max_length=255)
    brand_id: int
    category_id: Optional[int] = None
    description: Optional[str] = None
    ingredients: Optional[str] = None
    image_url: Optional[str] = None
    energy_type: str = Field("regular", description="Type: alcoholic, regular, sugar_free")
    average_rating: Optional[float] = None
    review_count: Optional[int] = None

class EnergyCreate(EnergyBase):
    pass

class Energy(EnergyBase):
    id: int
    brand: Brand
    category: Optional[Category]
    class Config:
        from_attributes = True

# в этой модели нет статистики брендов, потому что это уже 
# для списка энергетиков, принадлежащих определенному бренду
class EnergiesByBrand(EnergyBase):
    id: int
    brand: BrandAndEnergies
    category: Optional[Category]
    class Config:
        from_attributes = True

# =============== ПОЛЬЗОВАТЕЛИ ===============
class UserBase(BaseModel):
    username: str = Field(..., max_length=100)
    email: str = Field(..., max_length=255)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=255)

class User(UserBase):
    id: int
    is_premium: bool
    created_at: datetime
    class Config:
        from_attributes = True

# =============== КРИТЕРИИ ===============
class CriteriaBase(BaseModel):
    name: str = Field(..., max_length=100)

class CriteriaCreate(CriteriaBase):
    pass

class Criteria(CriteriaBase):
    id: int
    class Config:
        from_attributes = True

# =============== ОТЗЫВЫ И ОЦЕНКИ ===============
class RatingBase(BaseModel):
    criteria_id: int
    rating_value: condecimal(ge=0, le=10, decimal_places=4)

class ReviewBase(BaseModel):
    energy_id: int
    user_id: int
    review_text: str

class ReviewCreate(ReviewBase):
    ratings: List[RatingBase]

class Review(ReviewBase):
    id: int
    created_at: datetime
    ratings: List["Rating"]
    class Config:
        from_attributes = True

class Rating(RatingBase):
    id: int
    review_id: int
    created_at: datetime
    class Config:
        from_attributes = True

# =============== ПРОФИЛЬ ===============
class UserProfile(BaseModel):
    user: User
    total_ratings: int
    average_rating: Optional[condecimal(ge=0, le=10, decimal_places=4)] = None
    favorite_brand: Optional[Brand] = None
    favorite_energy: Optional[Energy] = None
    class Config:
        from_attributes = True

# =============== ТОПЫ ===============
class EnergyTop(BaseModel):
    id: int  # ID энергетика
    name: str  # Название энергетика
    average_rating: condecimal(ge=0, le=10, decimal_places=4)  # Средний рейтинг энергетика от 0 до 10 с 4 знаками после запятой
    brand: Brand  # Бренд энергетика
    category: Optional[Category] = None  # Категория энергетика (может быть None)
    review_count: int  # Общее количество записей в таблице Review

    class Config:
        from_attributes = True  # Разрешаем использование ORM-моделей

class BrandTop(BaseModel):
    id: int
    name: str
    average_rating: condecimal(ge=0, le=10, decimal_places=4)
    energy_count: Optional[int] = None
    review_count: Optional[int] = None
    rating_count: Optional[int] = None
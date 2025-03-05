from pydantic import BaseModel, constr, condecimal
from typing import Optional, List
from datetime import datetime


# =============== БРЕНДЫ ===============
class BrandBase(BaseModel):
    """ Базовая схема бренда энергетиков """
    name: constr(max_length=255)

class BrandCreate(BrandBase):
    """ Схема для создания нового бренда """
    pass

class Brand(BrandBase):
    """ Схема для представления бренда в ответе """
    id: int

    class Config:
        from_attributes = True


# =============== КАТЕГОРИИ ЭНЕРГЕТИКОВ ===============
class CategoryBase(BaseModel):
    """ Базовая схема категории энергетиков """
    name: constr(max_length=100)

class CategoryCreate(CategoryBase):
    """ Схема для создания новой категории """
    pass

class Category(CategoryBase):
    """ Схема для представления категории в ответе """
    id: int

    class Config:
        from_attributes = True


# =============== ЭНЕРГЕТИКИ ===============
class EnergyBase(BaseModel):
    """ Базовая схема энергетика """
    name: constr(max_length=255)
    description: Optional[str] = None
    ingredients: Optional[str] = None
    image_url: Optional[str] = None

class EnergyCreate(EnergyBase):
    """ Схема для создания нового энергетика """
    brand_id: int
    category_id: Optional[int] = None

class Energy(EnergyBase):
    """ Схема для представления энергетика в ответе """
    id: int
    brand: Brand
    category: Optional[Category]

    class Config:
        from_attributes = True


# =============== ПОЛЬЗОВАТЕЛИ ===============
class UserBase(BaseModel):
    """ Базовая схема пользователя """
    username: constr(max_length=100)
    email: constr(max_length=255)

class UserCreate(UserBase):
    """ Схема для регистрации нового пользователя """
    password: constr(min_length=8, max_length=255)

class User(UserBase):
    """ Схема для представления пользователя в ответе """
    id: int
    is_premium: bool
    created_at: datetime

    class Config:
        from_attributes = True


# =============== РОЛИ ===============
class RoleBase(BaseModel):
    """ Базовая схема роли пользователя """
    name: constr(max_length=50)

class RoleCreate(RoleBase):
    """ Схема для создания новой роли """
    pass

class Role(RoleBase):
    """ Схема для представления роли в ответе """
    id: int

    class Config:
        from_attributes = True


# =============== ОЦЕНКИ И ОТЗЫВЫ ===============
class RatingBase(BaseModel):
    """ Базовая схема оценки энергетика """
    rating: condecimal(max_digits=3, decimal_places=1)  # Оценка от 0.0 до 10.0
    review: Optional[str] = None

class RatingCreate(RatingBase):
    """ Схема для создания новой оценки """
    user_id: int
    energy_id: int
    criteria_id: int

class Rating(RatingBase):
    """ Схема для представления оценки в ответе """
    id: int
    user: User
    energy: Energy
    criteria: "Criteria"
    created_at: datetime

    class Config:
        from_attributes = True


# =============== КРИТЕРИИ ОЦЕНОК ===============
class CriteriaBase(BaseModel):
    """ Базовая схема критерия оценки """
    name: constr(max_length=100)

class CriteriaCreate(CriteriaBase):
    """ Схема для создания нового критерия """
    pass

class Criteria(CriteriaBase):
    """ Схема для представления критерия в ответе """
    id: int

    class Config:
        from_attributes = True


# =============== ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ (СТАТИСТИКА) ===============
class UserProfile(BaseModel):
    """ Схема профиля пользователя со статистикой """
    user: User
    total_ratings: int  # Количество оцененных энергетиков
    average_rating: Optional[condecimal(max_digits=3, decimal_places=1)] = None  # Средний балл всех оценок
    favorite_brand: Optional[Brand] = None  # Любимый бренд
    favorite_energy: Optional[Energy] = None  # Любимый энергетик

    class Config:
        from_attributes = True


# =============== ТОП ЭНЕРГЕТИКОВ ===============
class EnergyTop(BaseModel):
    """ Схема для отображения топа энергетиков """
    energy: Energy
    average_rating: condecimal(max_digits=3, decimal_places=1)

    class Config:
        from_attributes = True


class BrandTop(BaseModel):
    """ Схема для отображения топа брендов энергетиков """
    brand: Brand
    average_rating: condecimal(max_digits=3, decimal_places=1)

    class Config:
        from_attributes = True

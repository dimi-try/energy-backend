from pydantic import BaseModel, constr
from typing import Optional


# =============== БРЕНДЫ ===============
class BrandBase(BaseModel):
    name: constr(max_length=64)

class BrandCreate(BrandBase):
    pass

class Brand(BrandBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True

# =============== ЭНЕРГЕТИКИ ===============
class EnergyBase(BaseModel):
    name: constr(max_length=64)
    brand_id: int
    description: Optional[str] = None

# Схема для создания новой записи
class EnergyCreate(EnergyBase):
    pass

# Схема для представления данных
class Energy(EnergyBase):
    id: int
    brand: Brand

    class Config:
        orm_mode = True
        from_attributes = True 


# # Pydantic модель для представления рейтинга и отзыва (Rating)
# class RatingModel(BaseModel):
#     # Уникальный идентификатор рейтинга
#     id: int
#     # Идентификатор пользователя, который оставил рейтинг
#     user_id: int
#     # Идентификатор энергетика, для которого оставлен рейтинг
#     energy_id: int
#     # Оценка энергетика (рейтинг) от пользователя (необязательное поле, может быть None)
#     rating: Optional[float]
#     # Текстовый отзыв пользователя (необязательное поле)
#     review: Optional[str]
#     # Идентификатор критерия оценки (например, разные критерии для оценки энергетиков, необязательное поле)
#     criteria_id: Optional[int]
#     # Время создания отзыва (необязательное поле)
#     created_at: Optional[str]
#     # Булевое поле, указывающее, является ли отзыв историческим (True или False)
#     is_history: bool
#     # Идентификатор оригинального рейтинга, если этот рейтинг является измененной версией предыдущего (необязательное поле)
#     original_rating_id: Optional[int]

# # Pydantic модель для представления пользователя (User)
# class UserModel(BaseModel):
#     # Уникальный идентификатор пользователя
#     id: int
#     # Имя пользователя
#     name: str
#     # Электронная почта пользователя
#     email: str
#     # Время создания аккаунта пользователя
#     created_at: str

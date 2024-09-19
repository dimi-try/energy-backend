from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    description: str

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    class Config:
        orm_mode = True

# from pydantic import BaseModel
# from typing import Optional

# # Pydantic модель для представления бренда (Brand)
# class BrandModel(BaseModel):
#     # Уникальный идентификатор бренда
#     id: int
#     # Название бренда
#     name: str

# # Pydantic модель для представления энергетика (Energetic)
# class EnergeticModel(BaseModel):
#     # Уникальный идентификатор энергетика
#     id: int
#     # Название энергетика (необязательное поле, может быть None)
#     name: Optional[str]
#     # Вложенная модель бренда (BrandModel) с информацией о бренде, к которому принадлежит энергетик
#     brand: BrandModel
#     # Средняя оценка (рейтинг) энергетика, представлена как число с плавающей точкой
#     rating: float

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

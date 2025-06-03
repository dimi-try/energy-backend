# Импортируем BaseModel из Pydantic для создания схем
from pydantic import BaseModel, condecimal
# Импортируем Optional для аннотации
from typing import Optional
# Импортируем базовую модель для энергетиков
from app.schemas.brand import Brand
# Импортируем схемы для брендов и категорий
from app.schemas.category import Category

# =============== ТОПЫ ===============
# Определяем раздел для моделей топов (энергетиков и брендов)

# Модель для топа энергетиков
class EnergyTop(BaseModel):
    # Поле id: уникальный идентификатор энергетика
    id: int
    # Поле name: название энергетика
    name: str
    # Поле average_rating: средний рейтинг энергетика, от 0 до 10 с 4 знаками после запятой
    average_rating: condecimal(ge=0, le=10, decimal_places=4)
    # Поле brand: объект бренда энергетика
    brand: Brand
    # Поле category: объект категории, необязательное
    category: Optional[Category] = None
    # Поле review_count: общее количество отзывов на энергетик
    review_count: int
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True

"""
Сноска для EnergyTop:
Эта модель используется в эндпоинте GET /top/energies/, который возвращает топ энергетиков.
Эндпоинт доступен всем пользователям.
"""

# Модель для топа брендов
class BrandTop(BaseModel):
    # Поле id: уникальный идентификатор бренда
    id: int
    # Поле name: название бренда
    name: str
    # Поле average_rating: средний рейтинг бренда, от 0 до 10 с 4 знаками после запятой
    average_rating: condecimal(ge=0, le=10, decimal_places=4)
    # Поле energy_count: количество энергетиков бренда, необязательное
    energy_count: Optional[int] = None
    # Поле review_count: количество отзывов на энергетики бренда, необязательное
    review_count: Optional[int] = None
    # Поле rating_count: количество оценок на энергетики бренда, необязательное
    rating_count: Optional[int] = None

"""
Сноска для BrandTop:
Эта модель используется в эндпоинте GET /top/brands/, который возвращает топ брендов.
Эндпоинт доступен всем пользователям.
"""
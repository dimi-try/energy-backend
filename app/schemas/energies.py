# Импортируем BaseModel из Pydantic для создания схем
from pydantic import BaseModel, Field
# Импортируем Optional и List для аннотации
from typing import Optional, List
# Импортируем схемы для брендов, категорий и отзывов
from app.schemas.brands import Brand, BrandAndEnergies
from app.schemas.categories import Category

# =============== ЭНЕРГЕТИКИ ===============
# Определяем раздел для моделей, связанных с энергетиками

# Базовая модель для энергетиков, содержит общие поля
class EnergyBase(BaseModel):
    # Поле name: название энергетика, обязательное, с максимальной длиной 255 символов
    name: str = Field(..., max_length=255)
    # Поле brand_id: идентификатор бренда, к которому относится энергетик, обязательное
    brand_id: int
    # Поле category_id: идентификатор категории, необязательное, по умолчанию None
    category_id: Optional[int] = None
    # Поле description: описание энергетика, необязательное, строка
    description: Optional[str] = None
    # Поле ingredients: ингредиенты энергетика, необязательное, строка
    ingredients: Optional[str] = None
    # Поле image_url: URL изображения энергетика, необязательное
    image_url: Optional[str] = None
    # Поле average_rating: средний рейтинг энергетика, необязательное
    average_rating: Optional[float] = None
    # Поле review_count: количество отзывов на энергетик, необязательное
    review_count: Optional[int] = None

# Модель для создания энергетика, наследуется от EnergyBase
class EnergyCreate(EnergyBase):
    # Наследуем все поля из EnergyBase без изменений, используется для POST-запросов
    pass

# Полная модель энергетика, используется для возврата данных об энергетике
class Energy(EnergyBase):
    # Поле id: уникальный идентификатор энергетика
    id: int
    # Поле brand: объект бренда, к которому относится энергетик
    brand: Brand
    # Поле category: объект категории, необязательное, может быть None
    category: Optional[Category]
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True

"""
Сноска для Energy:
Эта модель используется в эндпоинтах GET /energies/ и GET /energy/{energy_id}.
- GET /energies/ возвращает список всех энергетиков, доступен всем пользователям.
- GET /energy/{energy_id} возвращает данные о конкретном энергетике, также доступен всем.
"""

# Модель для энергетиков бренда, без статистики бренда
class EnergiesByBrand(EnergyBase):
    # Поле id: уникальный идентификатор энергетика
    id: int
    # Поле brand: объект бренда без статистики, используется в списке энергетиков бренда
    brand: BrandAndEnergies
    # Поле category: объект категории, необязательное
    category: Optional[Category]
    # Внутренний класс Config для настройки модели
    class Config:
        # Указываем, что модель может быть создана из атрибутов ORM-объектов SQLAlchemy
        from_attributes = True

"""
Сноска для EnergiesByBrand:
Эта модель используется в эндпоинте GET /brands/{brand_id}/energies/, который возвращает
список энергетиков конкретного бренда. Доступен всем пользователям.
"""
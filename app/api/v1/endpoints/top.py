# Импортируем APIRouter из FastAPI для создания маршрутов
from fastapi import APIRouter, Depends
# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем List из typing для аннотации списков
from typing import List
# Импортируем функции для получения топов
from app.services.top import get_top_energies, get_top_brands
# Импортируем схемы для топов
from app.schemas.top import EnergyTop, BrandTop
# Импортируем зависимость для получения сессии базы данных
from app.db.database import get_db

# Создаём маршрутизатор для эндпоинтов топов
router = APIRouter()

# Определяем эндпоинт для получения топа энергетиков
@router.get("/energies/", response_model=List[EnergyTop])
def get_top_energies_endpoint(
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения топа энергетиков с наивысшим средним рейтингом.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию для получения топа энергетиков
    results = get_top_energies(db)
    # Возвращаем результаты
    return results

# Определяем эндпоинт для получения топа брендов
@router.get("/brands/", response_model=List[BrandTop])
def get_top_brands_endpoint(
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения топа брендов с наивысшим средним рейтингом.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию для получения топа брендов
    return get_top_brands(db)
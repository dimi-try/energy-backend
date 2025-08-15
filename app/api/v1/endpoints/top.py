from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db

from app.schemas.top import EnergyTop, BrandTop

from app.services.top import get_top_energies, get_top_brands

# Создаём маршрутизатор для эндпоинтов топов
router = APIRouter()

# =============== READ ENERGY CHART ===============
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

# =============== READ BRAND CHART ===============
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
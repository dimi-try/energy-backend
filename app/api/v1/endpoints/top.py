from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db

from app.schemas.top import EnergyTop, BrandTop

from app.services.top import get_top_energies, get_top_brands, get_total_energies, get_total_brands

# Создаём маршрутизатор для эндпоинтов топов
router = APIRouter()

# =============== READ ENERGY CHART ===============
@router.get("/energies/", response_model=List[EnergyTop])
def get_top_energies_endpoint(
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),           # Ограничиваем количество записей на страницу
    offset: int = Query(0, ge=0),                   # Смещение для пагинации
    search_query: str = Query(None),                # Поиск по названию энергетика или бренда
    min_rating: float = Query(None, ge=0, le=10),   # Минимальный рейтинг
    max_rating: float = Query(None, ge=0, le=10),   # Максимальный рейтинг
):
    """
    Эндпоинт для получения топа энергетиков с наивысшим 
    средним рейтингом с фильтрацией по названию и рейтингу.
    Доступен всем пользователям (гостям, зарегистрированным 
    пользователям и администраторам).
    """
    # Вызываем функцию для получения топа энергетиков
    results = get_top_energies(
        db,
        limit=limit,
        offset=offset,
        search_query=search_query,
        min_rating=min_rating,
        max_rating=max_rating
    )
    # Возвращаем результаты
    return results

# =============== READ BRAND CHART ===============
@router.get("/brands/", response_model=List[BrandTop])
def get_top_brands_endpoint(
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),           # Ограничиваем количество записей на страницу
    offset: int = Query(0, ge=0),                   # Смещение для пагинации
    search_query: str = Query(None),                # Поиск по названию бренда
    min_rating: float = Query(None, ge=0, le=10),   # Минимальный рейтинг
    max_rating: float = Query(None, ge=0, le=10),   # Максимальный рейтинг
):
    """
    Эндпоинт для получения топа брендов с фильтрацией по названию и рейтингу.
    """
    # Вызываем функцию для получения топа брендов
    return get_top_brands(
        db,
        limit=limit,
        offset=offset,
        search_query=search_query,
        min_rating=min_rating,
        max_rating=max_rating
    )

# =============== READ TOTAL ENERGY COUNT ===============
@router.get("/energies/count/")
def get_total_energies_endpoint(
    db: Session = Depends(get_db),
    search_query: str = Query(None),
    min_rating: float = Query(None, ge=0, le=10),
    max_rating: float = Query(None, ge=0, le=10),
):
    """
    Эндпоинт для получения общего количества энергетиков с учетом фильтров.
    """
    return {"total": get_total_energies(db, search_query, min_rating, max_rating)}

# =============== READ TOTAL BRAND COUNT ===============
@router.get("/brands/count/")
def get_total_brands_endpoint(
    db: Session = Depends(get_db),
    search_query: str = Query(None),
    min_rating: float = Query(None, ge=0, le=10),
    max_rating: float = Query(None, ge=0, le=10),
):
    """
    Эндпоинт для получения общего количества брендов с учетом фильтров.
    """
    return {"total": get_total_brands(db, search_query, min_rating, max_rating)}
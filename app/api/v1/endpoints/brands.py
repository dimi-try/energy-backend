# Импортируем APIRouter из FastAPI для создания маршрутов
from fastapi import APIRouter, Depends, HTTPException
# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем List из typing для аннотации списков
from typing import List
# Импортируем функции CRUD для брендов
from app.services.brands import get_brand, get_brands
from app.services.energies import get_energies_by_brand
# Импортируем схемы для брендов
from app.schemas.brand import Brand
from app.schemas.energy import EnergiesByBrand
# Импортируем зависимость для получения сессии базы данных
from app.db.database import get_db

# Создаём маршрутизатор для эндпоинтов брендов
router = APIRouter()

# Закомментированный эндпоинт для списка всех брендов (сохранён как есть)
# # Список всех брендов
# @router.get("/", response_model=List[schemas.Brand])
# def read_brands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return crud.get_brands(db, skip=skip, limit=limit)

# Определяем эндпоинт для получения данных о конкретном бренде
@router.get("/{brand_id}", response_model=Brand)
def read_brand(
    # Параметр пути: ID бренда
    brand_id: int,
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения данных о бренде по его ID.
    Возвращает объект Brand с дополнительными полями: average_rating, energy_count, review_count, rating_count.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию для получения данных о бренде
    db_brand = get_brand(db, brand_id=brand_id)
    # Проверяем, существует ли бренд
    if not db_brand:
        # Вызываем исключение, если бренд не найден
        raise HTTPException(status_code=404, detail="Brand not found")
    # Возвращаем объект бренда
    return db_brand

# Определяем эндпоинт для получения списка энергетиков бренда
@router.get("/{brand_id}/energies", response_model=List[EnergiesByBrand])
def read_energies_by_brand(
    # Параметр пути: ID бренда
    brand_id: int,
    # Параметр запроса: смещение для пагинации
    skip: int = 0,
    # Параметр запроса: лимит записей
    limit: int = 100,
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения списка энергетиков, принадлежащих определенному бренду,
    с пагинацией и сортировкой по рейтингу.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию для получения списка энергетиков бренда
    return get_energies_by_brand(db, brand_id=brand_id, skip=skip, limit=limit)
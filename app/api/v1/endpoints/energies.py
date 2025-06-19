# Импортируем APIRouter из FastAPI для создания маршрутов
from fastapi import APIRouter, Depends, HTTPException
# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем List из typing для аннотации списков
from typing import List
# Импортируем функции CRUD для энергетиков
from app.services.energies import get_energies, get_energy
from app.services.reviews import get_reviews_by_energy
# Импортируем схемы для энергетиков
from app.schemas.energy import Energy, EnergiesByBrand
from app.schemas.review import Review
# Импортируем зависимость для получения сессии базы данных
from app.db.database import get_db

# Создаём маршрутизатор для эндпоинтов энергетиков
router = APIRouter()

# Определяем эндпоинт для получения списка всех энергетиков
@router.get("/", response_model=List[Energy])
def read_energies(
    # Параметр запроса: смещение для пагинации
    skip: int = 0,
    # Параметр запроса: лимит записей
    limit: int = 100,
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения списка всех энергетиков с пагинацией.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию для получения списка энергетиков
    return get_energies(db, skip=skip, limit=limit)

# Определяем эндпоинт для получения данных о конкретном энергетике
@router.get("/{energy_id}", response_model=Energy)
def read_energy(
    # Параметр пути: ID энергетика
    energy_id: int,
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения данных об энергетике по его ID.
    Возвращает объект Energy с полем average_rating.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию для получения данных об энергетике
    db_energy = get_energy(db, energy_id=energy_id)
    # Проверяем, существует ли энергетик
    if not db_energy:
        # Вызываем исключение, если энергетик не найден
        raise HTTPException(status_code=404, detail="Energy not found")
    # Возвращаем объект энергетика
    return db_energy

# Определяем эндпоинт для получения списка отзывов на энергетик
@router.get("/{energy_id}/reviews", response_model=List[Review])
def read_energy_reviews(
    # Параметр пути: ID энергетика
    energy_id: int,
    # Параметр запроса: смещение для пагинации
    skip: int = 0,
    # Параметр запроса: лимит записей
    limit: int = 100,
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения списка отзывов на конкретный энергетик с пагинацией.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию для получения списка отзывов
    return get_reviews_by_energy(db, energy_id=energy_id, skip=skip, limit=limit)
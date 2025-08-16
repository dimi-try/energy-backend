from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordBearer

from app.core.auth import verify_admin_token

from app.db.database import get_db

from app.schemas.energies import Energy, EnergyCreate, EnergyUpdate
from app.schemas.reviews import ReviewWithRatings

from app.services.energies import get_energies, get_energy, create_energy, update_energy, delete_energy, get_energies_admin
from app.services.reviews import get_reviews_by_energy

# Создаём маршрутизатор для эндпоинтов энергетиков
router = APIRouter()

# Настройка OAuth2 для проверки JWT-токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/verify")

# =============== READ ALL ===============
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

# =============== READ ONE ===============
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

# =============== READ ALL REVIEWS ONE ENERGY ===============
@router.get("/{energy_id}/reviews", response_model=List[ReviewWithRatings])
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

# =============== ONLY ADMINS ===============

# =============== CREATE ===============
@router.post("/", response_model=Energy, status_code=status.HTTP_201_CREATED)
def create_new_energy(
    energy: EnergyCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Эндпоинт для создания нового энергетика.
    Доступен только администраторам.
    """
    verify_admin_token(token, db)
    db_energy = create_energy(db, energy)
    return db_energy

# =============== READ ALL WITHOUT PAGINATION ===============
@router.get("/admin/", response_model=List[Energy])
def read_energies_admin(
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения списка всех энергетиков без пагинации для админ-панели.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию для получения списка энергетиков
    return get_energies_admin(db)

# =============== UPDATE ===============
@router.put("/{energy_id}", response_model=Energy)
def update_existing_energy(
    energy_id: int,
    energy_update: EnergyUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Эндпоинт для обновления данных энергетика по его ID.
    Доступен только администраторам.
    """
    verify_admin_token(token, db)
    db_energy = update_energy(db, energy_id, energy_update)
    if not db_energy:
        raise HTTPException(status_code=404, detail="Energy not found")
    return db_energy

# =============== DELETE ===============
@router.delete("/{energy_id}", response_model=dict)
def delete_existing_energy(
    energy_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Эндпоинт для удаления энергетика по его ID.
    Доступен только администраторам.
    """
    verify_admin_token(token, db)
    success = delete_energy(db, energy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Energy not found")
    return {"success": True, "message": "Energy deleted successfully"}
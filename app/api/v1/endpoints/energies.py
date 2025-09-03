from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordBearer
from fastapi import Query
import os

from app.core.auth import verify_admin_token
from app.core.config import UPLOAD_DIR_ENERGY
from app.core.file_utils import validate_file, upload_file

from app.db.database import get_db

from app.schemas.energies import Energy, EnergyCreate, EnergyUpdate
from app.schemas.reviews import ReviewWithRatings

from app.services.energies import (
    get_energies, 
    get_energy, 
    create_energy, 
    update_energy, 
    delete_energy, 
    get_energies_admin, 
    get_reviews_by_energy, 
    get_total_reviews_by_energy,
    get_total_energies_admin,
)

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
    limit: int = 10,
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
    offset: int = Query(0, ge=0),
    # Параметр запроса: лимит записей
    limit: int = Query(10, ge=1, le=10),
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения списка отзывов на конкретный энергетик с пагинацией.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию для получения списка отзывов
    return get_reviews_by_energy(db, energy_id=energy_id, skip=offset, limit=limit)

# =============== READ TOTAL REVIEWS COUNT FOR ENERGY ===============
@router.get("/{energy_id}/reviews/count/")
def get_total_reviews_by_energy_endpoint(
    energy_id: int,
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения общего количества отзывов на энергетик.
    Доступен всем пользователям.
    """
    return {"total": get_total_reviews_by_energy(db, energy_id=energy_id)}

# =============== ONLY ADMINS ===============

# =============== UPLOAD IMAGE ===============
@router.post("/upload-image/")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    verify_admin_token(token, db)
    return await upload_file(file, UPLOAD_DIR_ENERGY)

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
    if energy.image_url and not os.path.exists(energy.image_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Указанный файл изображения не существует"
        )
    db_energy = create_energy(db, energy)
    return db_energy

# =============== READ ALL ADMIN ===============
@router.get("/admin/", response_model=List[Energy])
def read_energies_admin(
    skip: int = Query(0, ge=0, description="Смещение для пагинации"),
    limit: int = Query(10, ge=1, le=100, description="Лимит записей на страницу"),
    search_query: str = Query(None, description="Поиск по названию бренда или энергетика"),
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения списка всех энергетиков с пагинацией и поиском по 
    названию бренда или энергетика для админ-панели.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию для получения списка энергетиков
    return get_energies_admin(db, skip=skip, limit=limit, search=search_query)

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
    if energy_update.image_url and not os.path.exists(energy_update.image_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Указанный файл изображения не существует"
        )
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

# =============== READ TOTAL ENERGIES COUNT FOR ADMIN ===============
@router.get("/admin/count/")
def get_total_energies_admin_endpoint(
    search_query: str = Query(None, description="Поиск по названию бренда или энергетика"),
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения общего количества энергетиков с учетом поиска.
    Доступен всем пользователям.
    """
    return {"total": get_total_energies_admin(db, search=search_query)}
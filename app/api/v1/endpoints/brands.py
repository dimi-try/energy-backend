from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordBearer
from fastapi import Query

from app.core.auth import verify_admin_token

from app.db.database import get_db

from app.schemas.brands import Brand, BrandCreate, BrandUpdate
from app.schemas.energies import EnergiesByBrand

from app.services.brands import (
    get_brand,
    get_brands,
    get_brands_admin,
    create_brand,
    update_brand,
    delete_brand,
    get_energies_by_brand,
    get_total_energies_by_brand,
    get_total_brands_admin,
)

# Создаём маршрутизатор для эндпоинтов брендов
router = APIRouter()

# Настройка OAuth2 для проверки JWT-токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/verify")

# =============== READ ALL ===============
@router.get("/", response_model=List[Brand])
def read_brands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Эндпоинт для получения списка всех брендов с пагинацией.
    Доступен всем пользователям.
    """
    return get_brands(db, skip=skip, limit=limit)

# =============== READ ONE ===============
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

# =============== READ ALL ENERGIES ONE BRAND===============
@router.get("/{brand_id}/energies", response_model=List[EnergiesByBrand])
def read_energies_by_brand(
    # Параметр пути: ID бренда
    brand_id: int,
    # Параметр запроса: смещение для пагинации
    offset: int = Query(0, ge=0),
    # Параметр запроса: лимит записей
    limit: int = Query(10, ge=1, le=10),
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения списка энергетиков, принадлежащих определенному бренду,
    с пагинацией и сортировкой по рейтингу.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию для получения списка энергетиков бренда
    return get_energies_by_brand(db, brand_id=brand_id, skip=offset, limit=limit)

# =============== READ TOTAL ENERGIES COUNT FOR BRAND ===============
@router.get("/{brand_id}/energies/count/")
def get_total_energies_by_brand_endpoint(
    brand_id: int,
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения общего количества энергетиков бренда.
    Доступен всем пользователям.
    """
    return {"total": get_total_energies_by_brand(db, brand_id=brand_id)}

# =============== ONLY ADMINS ===============

# =============== CREATE ===============
@router.post("/", response_model=Brand, status_code=status.HTTP_201_CREATED)
def create_new_brand(
    brand: BrandCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Эндпоинт для создания нового бренда.
    Доступен только администраторам.
    """
    verify_admin_token(token, db)
    db_brand = create_brand(db, brand)
    return db_brand

# =============== READ ALL ADMIN ===============
@router.get("/admin/", response_model=List[Brand])
def read_brands_admin(
    skip: int = Query(0, ge=0, description="Смещение для пагинации"),
    limit: int = Query(10, ge=1, le=100, description="Лимит записей на страницу"),
    search_query: str = Query(None, description="Поиск по названию бренда"),
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения списка всех брендов с пагинацией и поиском для админ-панели.
    Доступен всем пользователям.
    """
    return get_brands_admin(db, skip=skip, limit=limit, search=search_query)

# =============== READ TOTAL BRANDS COUNT FOR ADMIN ===============
@router.get("/admin/count/")
def get_total_brands_admin_endpoint(
    search_query: str = Query(None, description="Поиск по названию бренда"),
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения общего количества брендов с учетом поиска.
    Доступен всем пользователям.
    """
    return {"total": get_total_brands_admin(db, search=search_query)}

# =============== UPDATE ===============
@router.put("/{brand_id}", response_model=Brand)
def update_existing_brand(
    brand_id: int,
    brand_update: BrandUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Эндпоинт для обновления данных бренда по его ID.
    Доступен только администраторам.
    """
    verify_admin_token(token, db)
    db_brand = update_brand(db, brand_id, brand_update)
    if not db_brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return db_brand

# =============== DELETE ===============
@router.delete("/{brand_id}", response_model=dict)
def delete_existing_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Эндпоинт для удаления бренда по его ID.
    Доступен только администраторам.
    """
    verify_admin_token(token, db)
    success = delete_brand(db, brand_id)
    if not success:
        raise HTTPException(status_code=404, detail="Brand not found")
    return {"success": True, "message": "Brand deleted successfully"}
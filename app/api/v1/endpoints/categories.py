from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordBearer

from app.core.auth import verify_admin_token

from app.db.database import get_db

from app.schemas.categories import Category, CategoryCreate, CategoryUpdate

from app.services.categories import get_categories, get_categories_admin, create_category, update_category, get_category_by_name

# Создаём маршрутизатор для эндпоинтов категорий
router = APIRouter()

# Настройка OAuth2 для проверки JWT-токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/verify")

# =============== READ ALL ===============
@router.get("/", response_model=List[Category])
def read_categories(
    # Параметр запроса: смещение для пагинации
    skip: int = 0,
    # Параметр запроса: лимит записей
    limit: int = 100,
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения списка всех категорий энергетиков с пагинацией.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию для получения списка категорий
    return get_categories(db, skip=skip, limit=limit)

# =============== ONLY ADMINS ===============

# =============== CREATE ===============
@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_new_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Эндпоинт для создания новой категории.
    Доступен только администраторам.
    """
    verify_admin_token(token, db)
    existing_category = get_category_by_name(db, category.name)
    if existing_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    return create_category(db, category)

# =============== READ ALL WITHOUT PAGINATION ===============
@router.get("/admin/", response_model=List[Category])
def read_categories_admin(
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения списка всех категорий энергетиков без пагинации для админ-панели.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию для получения списка категорий
    return get_categories_admin(db)

# =============== UPDATE ===============
@router.put("/{category_id}", response_model=Category)
def update_existing_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Эндпоинт для обновления данных категории по его ID.
    Доступен только администраторам.
    """
    verify_admin_token(token, db)
    try:
        db_category = update_category(db, category_id, category_update)
        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found")
        return db_category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
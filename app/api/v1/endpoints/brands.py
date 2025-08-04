# Импортируем APIRouter из FastAPI для создания маршрутов
from fastapi import APIRouter, Depends, HTTPException, status
# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем List из typing для аннотации списков
from typing import List
# Импортируем функции CRUD для брендов
from app.services.brands import get_brand, get_brands, create_brand, update_brand, delete_brand
from app.services.energies import get_energies_by_brand
# Импортируем схемы для брендов
from app.schemas.brands import Brand, BrandCreate, BrandUpdate
from app.schemas.energies import EnergiesByBrand
# Импортируем зависимость для получения сессии базы данных
from app.db.database import get_db
# Импортируем функции безопасности
from app.core.security import verify_admin_token
from fastapi.security import OAuth2PasswordBearer

# Создаём маршрутизатор для эндпоинтов брендов
router = APIRouter()

# Настройка OAuth2 для проверки JWT-токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/verify")

# Список всех брендов
@router.get("/", response_model=List[Brand])
def read_brands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Эндпоинт для получения списка всех брендов с пагинацией.
    Доступен всем пользователям.
    """
    return get_brands(db, skip=skip, limit=limit)

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

# Создание нового бренда (только для админов)
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

# Обновление бренда (только для админов)
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

# Удаление бренда (только для админов)
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
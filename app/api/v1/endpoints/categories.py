# Импортируем APIRouter из FastAPI для создания маршрутов
from fastapi import APIRouter, Depends, HTTPException, status
# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем List из typing для аннотации списков
from typing import List
# Импортируем функции CRUD для категорий
from app.services.categories import get_categories, create_category
# Импортируем схемы для категорий
from app.schemas.categories import Category, CategoryCreate
# Импортируем зависимость для получения сессии базы данных
from app.db.database import get_db

# Создаём маршрутизатор для эндпоинтов категорий
router = APIRouter()

# Закомментированный эндпоинт для создания категории (сохранён как есть)
# # Создание категории энегетиков
# @router.post("/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
# def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
#     db_category = crud.get_category_by_name(db, name=category.name)
#     if db_category:
#         raise HTTPException(status_code=400, detail="Category already exists")
#     return crud.create_category(db=db, category=category)

# Определяем эндпоинт для получения списка всех категорий
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
# Импортируем APIRouter из FastAPI для создания маршрутов
from fastapi import APIRouter, Depends, HTTPException, status
# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем List из typing для аннотации списков
from typing import List
# Импортируем функции CRUD для критериев
from app.services.criteria import get_all_criteria, create_criteria
# Импортируем схемы для критериев
from app.schemas.criteria import Criteria, CriteriaCreate
# Импортируем зависимость для получения сессии базы данных
from app.db.database import get_db

# Создаём маршрутизатор для эндпоинтов критериев
router = APIRouter()

# Закомментированный эндпоинт для создания критерия (сохранён как есть)
# # Создание критерия оценок
# @router.post("/", response_model=schemas.Criteria, status_code=status.HTTP_201_CREATED)
# def create_criteria(criteria: schemas.CriteriaCreate, db: Session = Depends(get_db)):
#     db_criteria = crud.get_criteria_by_name(db, name=criteria.name)
#     if db_criteria:
#         raise HTTPException(status_code=400, detail="Criteria already exists")
#     return crud.create_criteria(db=db, criteria=criteria)

# Определяем эндпоинт для получения списка всех критериев
@router.get("/", response_model=List[Criteria])
def read_all_criteria(
    # Параметр запроса: смещение для пагинации
    skip: int = 0,
    # Параметр запроса: лимит записей
    limit: int = 100,
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения списка всех критериев оценок с пагинацией.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию для получения списка критериев
    return get_all_criteria(db, skip=skip, limit=limit)
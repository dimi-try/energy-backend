from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordBearer

from app.core.auth import verify_admin_token

from app.db.database import get_db

from app.schemas.criteria import Criteria, CriteriaUpdate

from app.services.criteria import get_all_criteria, update_criteria

# Создаём маршрутизатор для эндпоинтов критериев
router = APIRouter()

# Настройка OAuth2 для проверки JWT-токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/verify")

# =============== READ ALL ===============
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

# =============== ONLY ADMINS ===============

# =============== UPDATE ===============
@router.put("/{criteria_id}", response_model=Criteria)
def update_existing_criteria(
    criteria_id: int,
    criteria_update: CriteriaUpdate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Эндпоинт для обновления данных критерия по его ID.
    Доступен только администраторам.
    """
    verify_admin_token(token, db)
    try:
        db_criteria = update_criteria(db, criteria_id, criteria_update)
        if not db_criteria:
            raise HTTPException(status_code=404, detail="Criteria not found")
        return db_criteria
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
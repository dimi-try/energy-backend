# Импортируем APIRouter из FastAPI для создания маршрутов
from fastapi import APIRouter, Depends, HTTPException, status
# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем List из typing для аннотации списков
from typing import List
# Импортируем функции CRUD для критериев
from app.services.criteria import get_all_criteria, create_criteria, update_criteria
# Импортируем схемы для критериев
from app.schemas.criteria import Criteria, CriteriaCreate, CriteriaUpdate
# Импортируем зависимость для получения сессии базы данных
from app.db.database import get_db
# Импортируем функции безопасности
from app.core.security import verify_admin_token
from fastapi.security import OAuth2PasswordBearer

# Создаём маршрутизатор для эндпоинтов критериев
router = APIRouter()

# Настройка OAuth2 для проверки JWT-токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/verify")

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

# Обновление критерия (только для админов)
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
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordBearer

from app.core.auth import verify_admin_token

from app.db.database import get_db

from app.schemas.blacklist import Blacklist, BlacklistCreate

from app.services.blacklist import create_blacklist_entry, get_all_blacklist_entries, delete_blacklist_entry
from app.services.users import get_user

# Создаём маршрутизатор для эндпоинтов черного списка
router = APIRouter()

# Настройка OAuth2 для проверки JWT-токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/verify")

# =============== ONLY ADMINS ===============

# =============== CREATE ===============
@router.post("/", response_model=Blacklist, status_code=status.HTTP_201_CREATED)
def add_to_blacklist(
    blacklist: BlacklistCreate,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Добавляет пользователя в черный список.
    Доступно только администраторам.
    """
    verify_admin_token(token, db)
    entry = create_blacklist_entry(db, blacklist)
    if not entry:
        raise HTTPException(status_code=400, detail="Пользователь уже находится в ЧС")
    # Проверяем, существует ли пользователь
    db_user = get_user(db, user_id=blacklist.user_id)
    if not db_user:
        return {"warning": "Пользователь незареган, но все равно добавлен в ЧС", **entry.__dict__}
    return entry

# =============== READ ALL ===============
@router.get("/", response_model=List[Blacklist])
def read_blacklist(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Получает список всех пользователей в черном списке.
    Доступно только администраторам.
    """
    verify_admin_token(token, db)
    entries = get_all_blacklist_entries(db, skip=skip, limit=limit)
    return entries

# =============== DELETE ===============
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_blacklist(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Удаляет пользователя из черного списка.
    Доступно только администраторам.
    """
    verify_admin_token(token, db)
    success = delete_blacklist_entry(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Пользователь не найден в черном списке")
    return None
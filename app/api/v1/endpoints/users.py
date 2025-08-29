from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordBearer

from app.core.auth import verify_token, verify_admin_token, get_current_user, get_user_role

from app.db.database import get_db

from app.schemas.users import User, UserCreate, UserProfile, UserReviews, UserUpdate

from app.services.users import get_user, create_user, get_user_profile, get_user_reviews, update_user, get_all_users, delete_user, get_total_reviews

# Создаём маршрутизатор для эндпоинтов пользователей
router = APIRouter()

# Настройка OAuth2 для проверки JWT-токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/verify")

# =============== READ ONE ===============
@router.get("/{user_id}", response_model=User)
def read_user(
    # Параметр пути: ID пользователя
    user_id: int,
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db),
    # Зависимость: текущий пользователь
    current_user: dict = Depends(get_current_user)
):
    """
    Эндпоинт для получения данных о пользователе по его ID.
    Доступен только самому пользователю или администраторам.
    """
    # Проверяем, что пользователь запрашивает свои данные
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user")
    # Вызываем функцию для получения данных о пользователе
    db_user = get_user(db, user_id=user_id)
    # Проверяем, существует ли пользователь
    if not db_user:
        # Вызываем исключение, если пользователь не найден
        raise HTTPException(status_code=404, detail="User not found")
    # Возвращаем объект пользователя
    return db_user

# =============== READ ONE PROFILE ===============
@router.get("/{user_id}/profile", response_model=UserProfile)
def get_user_profile_endpoint(
    # Параметр пути: ID пользователя
    user_id: int,
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db),
    # Зависимость: текущий пользователь
    current_user: dict = Depends(get_current_user)
):
    """
    Эндпоинт для получения профиля пользователя, включая статистику по оценкам.
    Доступен только самому пользователю или администраторам.
    """
    # Проверяем, что пользователь запрашивает свой профиль
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this profile")
    # Вызываем функцию для получения профиля пользователя
    profile = get_user_profile(db, user_id=user_id)
    # Проверяем, существует ли профиль
    if not profile:
        # Вызываем исключение, если профиль не найден
        raise HTTPException(status_code=404, detail="Profile not found")
    # Возвращаем профиль пользователя
    return profile

# =============== UPDATE ONE PROFILE ===============
@router.put("/{user_id}/profile", response_model=User)
def update_user_profile(
    # Параметр пути: ID пользователя
    user_id: int,
    # Тело запроса: данные для обновления
    user_update: UserUpdate,
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db),
    # Зависимость: текущий пользователь
    current_user: dict = Depends(get_current_user)
):
    """
    Эндпоинт для редактирования профиля пользователя (username).
    Доступен только самому пользователю.
    """
    # Проверяем, что пользователь редактирует свой профиль
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this profile")
    # Вызываем функцию для обновления пользователя
    updated_user = update_user(db, user_id=user_id, user_update=user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

# =============== READ ALL REVIEWS ONE USER===============
@router.get("/{user_id}/reviews", response_model=UserReviews)
def get_user_reviews_endpoint(
    # Параметр пути: ID пользователя
    user_id: int,
    # Параметры пагинации
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db),
    # Зависимость: текущий пользователь
    current_user: dict = Depends(get_current_user)
):
    """
    Эндпоинт для получения отзывов пользователя.
    Доступен только самому пользователю или администраторам.
    """
    # Проверяем, что пользователь запрашивает свои отзывы
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access these reviews")
    # Вызываем функцию для получения отзывов пользователя
    reviews = get_user_reviews(db, user_id=user_id, skip=offset, limit=limit)
    # Проверяем, существуют ли отзывы
    if not reviews:
        # Вызываем исключение, если отзывы не найдены
        raise HTTPException(status_code=404, detail="Reviews not found")
    # Возвращаем отзывы пользователя
    return reviews

# =============== READ TOTAL REVIEWS COUNT ===============
@router.get("/{user_id}/reviews/count/")
def get_total_reviews_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Эндпоинт для получения общего количества отзывов пользователя.
    Доступен только самому пользователю или администраторам.
    """
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access these reviews")
    return {"total": get_total_reviews(db, user_id=user_id)}

# =============== READ OWN ROLE ===============
@router.get("/me/role", response_model=dict)
def get_user_role_endpoint(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Эндпоинт для получения роли текущего пользователя.
    """
    role = get_user_role(db, user_id=current_user["user_id"])
    return {"role": role}

# =============== UPLOAD USER IMAGE ===============
@router.post("/upload-image/")
async def upload_user_image(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return await upload_file(file, UPLOAD_DIR_USER)

# =============== ONLY ADMINS ===============

# =============== READ ALL ===============
@router.get("/", response_model=List[User])
def read_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Эндпоинт для получения списка всех пользователей с пагинацией.
    Доступен только администраторам.
    """
    verify_admin_token(token, db)
    return get_all_users(db, skip=skip, limit=limit)

# =============== DELETE ===============
@router.delete("/{user_id}", response_model=dict)
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Эндпоинт для удаления пользователя по его ID.
    Доступен только администраторам.
    """
    verify_admin_token(token, db)
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "message": "User deleted successfully"}
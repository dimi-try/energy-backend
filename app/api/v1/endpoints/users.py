# Импортируем APIRouter из FastAPI для создания маршрутов
from fastapi import APIRouter, Depends, HTTPException, status
# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем функции CRUD для пользователей
from app.services.users import get_user, create_user, get_user_profile, get_user_reviews
# Импортируем схемы для пользователей
from app.schemas.users import User, UserCreate, UserProfile, UserReviews
# Импортируем зависимость для получения сессии базы данных
from app.db.database import get_db

# Создаём маршрутизатор для эндпоинтов пользователей
router = APIRouter()

# Определяем эндпоинт для получения данных о пользователе
@router.get("/{user_id}", response_model=User)
def read_user(
    # Параметр пути: ID пользователя
    user_id: int,
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения данных о пользователе по его ID.
    Доступен только самому пользователю или администраторам.
    """
    # Вызываем функцию для получения данных о пользователе
    db_user = get_user(db, user_id=user_id)
    # Проверяем, существует ли пользователь
    if not db_user:
        # Вызываем исключение, если пользователь не найден
        raise HTTPException(status_code=404, detail="User not found")
    # Возвращаем объект пользователя
    return db_user

# Определяем эндпоинт для получения профиля пользователя
@router.get("/{user_id}/profile", response_model=UserProfile)
def get_user_profile_endpoint(
    # Параметр пути: ID пользователя
    user_id: int,
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения профиля пользователя, включая статистику по оценкам.
    Доступен только самому пользователю или администраторам.
    """
    # Вызываем функцию для получения профиля пользователя
    profile = get_user_profile(db, user_id=user_id)
    # Проверяем, существует ли профиль
    if not profile:
        # Вызываем исключение, если профиль не найден
        raise HTTPException(status_code=404, detail="Profile not found")
    # Возвращаем профиль пользователя
    return profile


# Определяем эндпоинт для получения отзывов пользователя
@router.get("/{user_id}/reviews", response_model=UserReviews)
def get_user_reviews_endpoint(
    # Параметр пути: ID пользователя
    user_id: int,
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для получения отзывов пользователя.
    Доступен только самому пользователю или администраторам.
    """
    # Вызываем функцию для получения отзывов пользователя
    reviews = get_user_reviews(db, user_id=user_id)
    # Проверяем, существуют ли отзывы
    if not reviews:
        # Вызываем исключение, если отзывы не найден
        raise HTTPException(status_code=404, detail="Reciews not found")
    # Возвращаем отзывы пользователя
    return reviews
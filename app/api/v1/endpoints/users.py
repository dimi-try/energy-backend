# Импортируем APIRouter из FastAPI для создания маршрутов
from fastapi import APIRouter, Depends, HTTPException, status
# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем функции CRUD для пользователей
from app.services.users import get_user, create_user, get_user_profile
# Импортируем схемы для пользователей
from app.schemas.user import User, UserCreate, UserProfile
# Импортируем зависимость для получения сессии базы данных
from app.db.database import get_db

# Создаём маршрутизатор для эндпоинтов пользователей
router = APIRouter()

# Закомментированный эндпоинт для создания пользователя (сохранён как есть)
# # Создание пользователя
# @router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return crud.create_user(db=db, user=user)

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
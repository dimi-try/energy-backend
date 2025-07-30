# Импортируем APIRouter из FastAPI для создания маршрутов
from fastapi import APIRouter, Depends, HTTPException, status
# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем List из typing для аннотации списков
from typing import List
# Импортируем функции CRUD для отзывов и пользователей
from app.services.reviews import create_review_with_ratings, get_review, update_review, delete_review
from app.services.ratings import get_ratings_by_review
# Импортируем функции для получения пользователя и отзыва по пользователю и энергетикам
from app.services.users import get_user, get_review_by_user_and_energy
# Импортируем функцию для получения энергетика
from app.services.energies import get_energy
# Импортируем схемы для отзывов
from app.schemas.reviews import Review, ReviewCreate, ReviewUpdate
# Импортируем зависимость для получения сессии базы данных
from app.db.database import get_db
# Импортируем функции безопасности
from app.core.security import verify_token
# Импортируем OAuth2PasswordBearer для работы с JWT
from fastapi.security import OAuth2PasswordBearer

# Создаём маршрутизатор для эндпоинтов отзывов
router = APIRouter()

# Настройка OAuth2 для проверки JWT-токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/verify")

# Зависимость для получения текущего пользователя из JWT-токена
def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Проверяет JWT-токен и возвращает данные текущего пользователя.
    """
    payload = verify_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: user_id not found")
    return {"user_id": int(user_id)}

# Определяем эндпоинт для создания отзыва
@router.post("/", response_model=Review, status_code=status.HTTP_201_CREATED)
def create_review(
    # Тело запроса: данные для создания отзыва
    review: ReviewCreate,
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db),
    # Зависимость: текущий пользователь
    current_user: dict = Depends(get_current_user)
):
    """
    Эндпоинт для создания отзыва с оценками.
    Доступен только зарегистрированным пользователям.
    Проверяет существование энергетика и пользователя, а также наличие существующего отзыва.
    """
    # Проверяем, что пользователь создает отзыв от своего имени
    if current_user["user_id"] != review.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to create review for another user")
    
    # Проверяем существование энергетика
    db_energy = get_energy(db, energy_id=review.energy_id)
    # Вызываем исключение, если энергетик не найден
    if not db_energy:
        raise HTTPException(status_code=404, detail="Energy not found")
    
    # Проверяем существование пользователя
    db_user = get_user(db, user_id=review.user_id)
    # Вызываем исключение, если пользователь не найден
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем, оставил ли пользователь уже отзыв на этот энергетик
    existing_review = get_review_by_user_and_energy(
        db, 
        user_id=review.user_id,
        energy_id=review.energy_id
    )
    # Вызываем исключение, если отзыв уже существует
    if existing_review:
        raise HTTPException(
            status_code=400,
            detail="User already has a review for this energy drink"
        )

    # Вызываем функцию для создания отзыва с оценками
    return create_review_with_ratings(db=db, review=review)

# Определяем эндпоинт для редактирования отзыва
@router.put("/{review_id}", response_model=Review)
def update_review_endpoint(
    # Параметр пути: ID отзыва
    review_id: int,
    # Тело запроса: данные для обновления отзыва
    review_update: ReviewUpdate,
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db),
    # Зависимость: текущий пользователь
    current_user: dict = Depends(get_current_user)
):
    """
    Эндпоинт для редактирования отзыва.
    Доступен только владельцу отзыва.
    """
    # Получаем отзыв
    db_review = get_review(db, review_id=review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    # Проверяем, что пользователь редактирует свой отзыв
    if db_review.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to edit this review")
    # Обновляем отзыв
    updated_review = update_review(db, review_id=review_id, review_update=review_update)
    if not updated_review:
        raise HTTPException(status_code=404, detail="Review not found")
    return updated_review

# Определяем эндпоинт для удаления отзыва
@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review_endpoint(
    # Параметр пути: ID отзыва
    review_id: int,
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db),
    # Зависимость: текущий пользователь
    current_user: dict = Depends(get_current_user)
):
    """
    Эндпоинт для удаления отзыва.
    Доступен только владельцу отзыва.
    """
    # Получаем отзыв
    db_review = get_review(db, review_id=review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    # Проверяем, что пользователь удаляет свой отзыв
    if db_review.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this review")
    # Удаляем отзыв
    success = delete_review(db, review_id=review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    return None
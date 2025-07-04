# Импортируем APIRouter из FastAPI для создания маршрутов
from fastapi import APIRouter, Depends, HTTPException, status
# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем List из typing для аннотации списков
from typing import List
# Импортируем функции CRUD для отзывов и пользователей
from app.services.reviews import create_review_with_ratings, get_review
from app.services.ratings import get_ratings_by_review
# Импортируем функции для получения пользователя и отзыва по пользователю и энергетикам
from app.services.users import get_user, get_review_by_user_and_energy
# Импортируем функцию для получения энергетика
from app.services.energies import get_energy
# Импортируем схемы для отзывов
from app.schemas.reviews import Review, ReviewCreate
# Импортируем зависимость для получения сессии базы данных
from app.db.database import get_db

# Создаём маршрутизатор для эндпоинтов отзывов
router = APIRouter()

# Определяем эндпоинт для создания отзыва
@router.post("/", response_model=Review, status_code=status.HTTP_201_CREATED)
def create_review(
    # Тело запроса: данные для создания отзыва
    review: ReviewCreate,
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для создания отзыва с оценками.
    Доступен только зарегистрированным пользователям.
    Проверяет существование энергетика и пользователя, а также наличие существующего отзыва.
    """
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

# Закомментированный эндпоинт для получения данных об отзыве (сохранён как есть)
# # Данные по конкретному отзыву
# @router.get("/{review_id}", response_model=schemas.Review)
# def read_review(review_id: int, db: Session = Depends(get_db)):
#     db_review = crud.get_review(db, review_id=review_id)
#     if not db_review:
#         raise HTTPException(status_code=404, detail="Review not found")
#     return db_review

# Закомментированный эндпоинт для получения оценок отзыва (сохранён как есть)
# # Данные о конкретном отзыве 
# @router.get("/{review_id}/ratings/", response_model=List[schemas.Rating])
# def read_review_ratings(review_id: int, db: Session = Depends(get_db)):
#     return crud.get_ratings_by_review(db, review_id=review_id)
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import OAuth2PasswordBearer
import os

from app.core.auth import verify_token, verify_admin_token, get_current_user
from app.core.config import UPLOAD_DIR_REVIEW
from app.core.file_utils import upload_file

from app.db.database import get_db

from app.schemas.reviews import Review, ReviewCreate, ReviewUpdate, ReviewWithRatings

from app.services.reviews import create_review_with_ratings, get_review, update_review, delete_review, get_all_reviews
from app.services.ratings import get_ratings_by_review
from app.services.users import get_user, get_review_by_user_and_energy
from app.services.energies import get_energy
from app.services.blacklist import get_blacklist_entry

# Создаём маршрутизатор для эндпоинтов отзывов
router = APIRouter()

# Настройка OAuth2 для проверки JWT-токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/verify")

# =============== CREATE ===============
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
    # Проверяем, находится ли пользователь в черном списке
    blacklist_entry = get_blacklist_entry(db, user_id=current_user["user_id"])
    if blacklist_entry:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Вы в черном списке по причине: {blacklist_entry.reason or 'Не указана'}"
        )
        
    # Проверяем, что пользователь создает отзыв от своего имени
    if current_user["user_id"] != review.user_id:
        raise HTTPException(status_code=403, detail="Пожалуйста, перезапустите бота и зайдите заново в приложение!")
    
    # Проверяем существование энергетика
    db_energy = get_energy(db, energy_id=review.energy_id)
    # Вызываем исключение, если энергетик не найден
    if not db_energy:
        raise HTTPException(status_code=404, detail="Энергетик не найден!")
    
    # Проверяем существование пользователя
    db_user = get_user(db, user_id=review.user_id)
    # Вызываем исключение, если пользователь не найден
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден!")
    
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
            detail="Вы уже оставили отзыв на этот энергетик! Вы можете отредактировать свой отзыв."
        )
    if not review.ratings:
        raise HTTPException(
            status_code=400,
            detail="Оценки обязательны для создания отзыва!"
        )
    if review.image_url and not os.path.exists(review.image_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Указанный файл изображения не существует"
        )
    # Вызываем функцию для создания отзыва с оценками
    return create_review_with_ratings(db=db, review=review)

# =============== UPDATE ===============
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
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    # Проверяем, что пользователь редактирует свой отзыв
    if db_review.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Пожалуйста, перезапустите бота и зайдите заново в приложение!")
    if review_update.image_url and not os.path.exists(review_update.image_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Указанный файл изображения не существует"
        )
    # Обновляем отзыв
    updated_review = update_review(db, review_id=review_id, review_update=review_update)
    if not updated_review:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    return updated_review

# =============== DELETE ===============
@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review_endpoint(
    # Параметр пути: ID отзыва
    review_id: int,
    # Зависимость: сессия базы данных
    db: Session = Depends(get_db),
    # Зависимость: текущий пользователь
    current_user: dict = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """
    Эндпоинт для удаления отзыва.
    Доступен владельцу отзыва или администраторам.
    """
    # Получаем отзыв
    db_review = get_review(db, review_id=review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    # Проверяем, что пользователь удаляет свой отзыв или является админом
    if db_review.user_id != current_user["user_id"]:
        verify_admin_token(token, db)
    # Удаляем отзыв
    success = delete_review(db, review_id=review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    return None

# =============== UPLOAD REVIEW IMAGE ===============
@router.post("/upload-image/")
async def upload_review_image(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return await upload_file(file, UPLOAD_DIR_REVIEW)

# =============== ONLY ADMINS ===============

# =============== READ ALL ===============
@router.get("/", response_model=List[ReviewWithRatings])
def read_all_reviews(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Эндпоинт для получения списка всех отзывов с пагинацией.
    Доступен только администраторам.
    """
    verify_admin_token(token, db)
    reviews = get_all_reviews(db, skip=skip, limit=limit)
    return reviews
# Импортируем APIRouter из FastAPI для создания маршрутов
from fastapi import APIRouter, Depends, HTTPException, status
# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем модули crud, models и schemas из текущего пакета
from . import crud, models, schemas
# Импортируем зависимости базы данных
from .database import SessionLocal, get_db
# Импортируем List из typing для аннотации списков в ответах
from typing import List

# Создаем объект маршрутизатора для определения эндпоинтов
router = APIRouter()

# ========================= BRANDS =========================
# Определяем раздел для эндпоинтов, связанных с брендами

# Закомментированный эндпоинт для списка всех брендов (оставляем как есть)
# # Список всех брендов
# @router.get("/brands/", response_model=List[schemas.Brand])
# def read_brands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     return crud.get_brands(db, skip=skip, limit=limit)

# Эндпоинт для получения данных о конкретном бренде
@router.get("/brand/{brand_id}", response_model=schemas.Brand)
def read_brand(brand_id: int, db: Session = Depends(get_db)):
    """
    Эндпоинт для получения данных о бренде по его ID.
    Возвращает объект Brand с дополнительными полями: average_rating, energy_count, review_count, rating_count.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию crud для получения данных о бренде
    db_brand = crud.get_brand(db, brand_id=brand_id)
    # Проверяем, существует ли бренд
    if not db_brand:
        # Если бренд не найден, вызываем исключение 404
        raise HTTPException(status_code=404, detail="Brand not found")
    # Возвращаем объект бренда
    return db_brand

# ========================= ENERGIES =========================
# Определяем раздел для эндпоинтов, связанных с энергетиками

# Эндпоинт для получения списка всех энергетиков
@router.get("/energies/", response_model=List[schemas.Energy])
def read_energies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Эндпоинт для получения списка всех энергетиков с пагинацией.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию crud для получения списка энергетиков
    return crud.get_energies(db, skip=skip, limit=limit)

# Эндпоинт для получения данных о конкретном энергетике
@router.get("/energy/{energy_id}", response_model=schemas.Energy)
def read_energy(energy_id: int, db: Session = Depends(get_db)):
    """
    Эндпоинт для получения данных об энергетике по его ID.
    Возвращает объект Energy с полем average_rating.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию crud для получения данных об энергетике
    db_energy = crud.get_energy(db, energy_id=energy_id)
    # Проверяем, существует ли энергетик
    if not db_energy:
        # Если энергетик не найден, вызываем исключение 404
        raise HTTPException(status_code=404, detail="Energy not found")
    # Возвращаем объект энергетика
    return db_energy

# Эндпоинт для получения списка энергетиков определенного бренда
@router.get("/brands/{brand_id}/energies/", response_model=List[schemas.EnergiesByBrand])
def read_energies_by_brand(brand_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Эндпоинт для получения списка энергетиков, принадлежащих определенному бренду,
    с пагинацией и сортировкой по рейтингу.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию crud для получения списка энергетиков бренда
    return crud.get_energies_by_brand(db, brand_id=brand_id, skip=skip, limit=limit)

# ========================= USERS =========================
# Определяем раздел для эндпоинтов, связанных с пользователями

# Закомментированный эндпоинт для создания пользователя (оставляем как есть)
# # Создание пользователя
# @router.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return crud.create_user(db=db, user=user)

# Эндпоинт для получения данных о конкретном пользователе
@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Эндпоинт для получения данных о пользователе по его ID.
    Доступен только самому пользователю или администраторам.
    """
    # Вызываем функцию crud для получения данных о пользователе
    db_user = crud.get_user(db, user_id=user_id)
    # Проверяем, существует ли пользователь
    if not db_user:
        # Если пользователь не найден, вызываем исключение 404
        raise HTTPException(status_code=404, detail="User not found")
    # Возвращаем объект пользователя
    return db_user

# ========================= REVIEWS =========================
# Определяем раздел для эндпоинтов, связанных с отзывами

# Эндпоинт для создания отзыва
@router.post("/review/", response_model=schemas.Review, status_code=status.HTTP_201_CREATED)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    """
    Эндпоинт для создания отзыва с оценками.
    Доступен только зарегистрированным пользователям.
    Проверяет существование энергетика и пользователя, а также наличие существующего отзыва.
    """
    # Проверяем существование энергетика
    db_energy = crud.get_energy(db, energy_id=review.energy_id)
    # Если энергетик не найден, вызываем исключение 404
    if not db_energy:
        raise HTTPException(status_code=404, detail="Energy not found")
    
    # Проверяем существование пользователя
    db_user = crud.get_user(db, user_id=review.user_id)
    # Если пользователь не найден, вызываем исключение 404
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем, оставил ли пользователь уже отзыв на этот энергетик
    existing_review = crud.get_review_by_user_and_energy(
        db, 
        user_id=review.user_id,
        energy_id=review.energy_id
    )
    # Если отзыв уже существует, вызываем исключение 400
    if existing_review:
        raise HTTPException(
            status_code=400,
            detail="User already has a review for this energy drink"
        )

    # Вызываем функцию crud для создания отзыва с оценками
    return crud.create_review_with_ratings(db=db, review=review)

# Закомментированный эндпоинт для получения данных об отзыве (оставляем как есть)
# # Данные по конкретному отзыву
# @router.get("/reviews/{review_id}", response_model=schemas.Review)
# def read_review(review_id: int, db: Session = Depends(get_db)):
#     db_review = crud.get_review(db, review_id=review_id)
#     if not db_review:
#         raise HTTPException(status_code=404, detail="Review not found")
#     return db_review

# Эндпоинт для получения списка отзывов на энергетик
@router.get("/energy/{energy_id}/reviews/", response_model=List[schemas.Review])
def read_energy_reviews(energy_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Эндпоинт для получения списка отзывов на конкретный энергетик с пагинацией.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию crud для получения списка отзывов
    return crud.get_reviews_by_energy(db, energy_id=energy_id, skip=skip, limit=limit)

# ========================= CRITERIA =========================
# Определяем раздел для эндпоинтов, связанных с критериями

# Закомментированный эндпоинт для создания критерия (оставляем как есть)
# # Создание критерия оценок
# @router.post("/criteria/", response_model=schemas.Criteria, status_code=status.HTTP_201_CREATED)
# def create_criteria(criteria: schemas.CriteriaCreate, db: Session = Depends(get_db)):
#     db_criteria = crud.get_criteria_by_name(db, name=criteria.name)
#     if db_criteria:
#         raise HTTPException(status_code=400, detail="Criteria already exists")
#     return crud.create_criteria(db=db, criteria=criteria)

# Эндпоинт для получения списка всех критериев
@router.get("/criteria/", response_model=List[schemas.Criteria])
def read_all_criteria(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Эндпоинт для получения списка всех критериев оценок с пагинацией.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию crud для получения списка критериев
    return crud.get_all_criteria(db, skip=skip, limit=limit)

# ========================= CATEGORIES =========================
# Определяем раздел для эндпоинтов, связанных с категориями

# Закомментированный эндпоинт для создания категории (оставляем как есть)
# # Создание категории энегетиков
# @router.post("/categories/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
# def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
#     db_category = crud.get_category_by_name(db, name=category.name)
#     if db_category:
#         raise HTTPException(status_code=400, detail="Category already exists")
#     return crud.create_category(db=db, category=category)

# Эндпоинт для получения списка всех категорий
@router.get("/categories/", response_model=List[schemas.Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Эндпоинт для получения списка всех категорий энергетиков с пагинацией.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию crud для получения списка категорий
    return crud.get_categories(db, skip=skip, limit=limit)

# ========================= USER PROFILE =========================
# Определяем раздел для эндпоинта профиля пользователя

# Эндпоинт для получения профиля пользователя
@router.get("/users/{user_id}/profile", response_model=schemas.UserProfile)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """
    Эндпоинт для получения профиля пользователя, включая статистику по оценкам.
    Доступен только самому пользователю или администраторам.
    """
    # Вызываем функцию crud для получения профиля
    profile = crud.get_user_profile(db, user_id=user_id)
    # Проверяем, существует ли профиль
    if not profile:
        # Если профиль не найден, вызываем исключение 404
        raise HTTPException(status_code=404, detail="Profile not found")
    # Возвращаем профиль пользователя
    return profile

# ========================= TOP RATINGS =========================
# Определяем раздел для эндпоинтов топов

# Эндпоинт для получения топа энергетиков
@router.get("/top/energies/", response_model=List[schemas.EnergyTop])
def get_top_energies(db: Session = Depends(get_db)):
    """
    Эндпоинт для получения топа энергетиков с наивысшим средним рейтингом.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию crud для получения топа энергетиков
    results = crud.get_top_energies(db)
    # Возвращаем результаты
    return results

# Эндпоинт для получения топа брендов
@router.get("/top/brands/", response_model=List[schemas.BrandTop])
def get_top_brands(db: Session = Depends(get_db)):
    """
    Эндпоинт для получения топа брендов с наивысшим средним рейтингом.
    Доступен всем пользователям (гостям, зарегистрированным пользователям и администраторам).
    """
    # Вызываем функцию crud для получения топа брендов
    return crud.get_top_brands(db)

# ========================= RATINGS =========================
# Определяем раздел для закомментированных эндпоинтов оценок (оставляем как есть)

# Закомментированный эндпоинт для получения данных об оценке
# # Данные о конкретной оценке
# @router.get("/ratings/{rating_id}", response_model=schemas.Rating)
# def read_rating(rating_id: int, db: Session = Depends(get_db)):
#     db_rating = crud.get_rating(db, rating_id=rating_id)
#     if not db_rating:
#         raise HTTPException(status_code=404, detail="Rating not found")
#     return db_rating

# Закомментированный эндпоинт для получения оценок отзыва
# # Данные о конкретном отзыве 
# @router.get("/reviews/{review_id}/ratings/", response_model=List[schemas.Rating])
# def read_review_ratings(review_id: int, db: Session = Depends(get_db)):
#     return crud.get_ratings_by_review(db, review_id=review_id)
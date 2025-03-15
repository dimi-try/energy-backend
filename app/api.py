from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, get_db
from typing import List

router = APIRouter()

# ========================= BRANDS =========================
@router.get("/brands/", response_model=List[schemas.Brand])
def read_brands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_brands(db, skip=skip, limit=limit)

@router.get("/brand/{brand_id}", response_model=schemas.Brand)
def read_brand(brand_id: int, db: Session = Depends(get_db)):
    db_brand = crud.get_brand(db, brand_id=brand_id)
    if not db_brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return db_brand

# ========================= ENERGIES =========================
@router.get("/energies/", response_model=List[schemas.Energy])
def read_energies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_energies(db, skip=skip, limit=limit)

@router.get("/energy/{energy_id}", response_model=schemas.Energy)
def read_energy(energy_id: int, db: Session = Depends(get_db)):
    db_energy = crud.get_energy(db, energy_id=energy_id)
    if not db_energy:
        raise HTTPException(status_code=404, detail="Energy not found")
    return db_energy

@router.get("/brands/{brand_id}/energies/", response_model=List[schemas.Energy])
def read_energies_by_brand(brand_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_energies_by_brand(db, brand_id=brand_id, skip=skip, limit=limit)

# ========================= USERS =========================
@router.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# ========================= REVIEWS =========================
@router.post("/reviews/", response_model=schemas.Review, status_code=status.HTTP_201_CREATED)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    # Проверка существования энергетика
    db_energy = crud.get_energy(db, energy_id=review.energy_id)
    if not db_energy:
        raise HTTPException(status_code=404, detail="Energy not found")
    
    # Проверка существования пользователя
    db_user = crud.get_user(db, user_id=review.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return crud.create_review_with_ratings(db=db, review=review)

@router.get("/reviews/{review_id}", response_model=schemas.Review)
def read_review(review_id: int, db: Session = Depends(get_db)):
    db_review = crud.get_review(db, review_id=review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    return db_review

@router.get("/energies/{energy_id}/reviews/", response_model=List[schemas.Review])
def read_energy_reviews(energy_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_reviews_by_energy(db, energy_id=energy_id, skip=skip, limit=limit)

# ========================= CRITERIA =========================
@router.post("/criteria/", response_model=schemas.Criteria, status_code=status.HTTP_201_CREATED)
def create_criteria(criteria: schemas.CriteriaCreate, db: Session = Depends(get_db)):
    db_criteria = crud.get_criteria_by_name(db, name=criteria.name)
    if db_criteria:
        raise HTTPException(status_code=400, detail="Criteria already exists")
    return crud.create_criteria(db=db, criteria=criteria)

@router.get("/criteria/", response_model=List[schemas.Criteria])
def read_all_criteria(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all_criteria(db, skip=skip, limit=limit)

# ========================= CATEGORIES =========================
@router.post("/categories/", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = crud.get_category_by_name(db, name=category.name)
    if db_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    return crud.create_category(db=db, category=category)

@router.get("/categories/", response_model=List[schemas.Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_categories(db, skip=skip, limit=limit)

# ========================= USER PROFILE =========================
@router.get("/users/{user_id}/profile", response_model=schemas.UserProfile)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    profile = crud.get_user_profile(db, user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

# ========================= TOP RATINGS =========================
@router.get("/top/energies/", response_model=List[schemas.EnergyTop])  # Определяем GET-запрос с указанием схемы ответа
def get_top_energies(db: Session = Depends(get_db)):  # Зависимость для получения сессии базы данных
    results = crud.get_top_energies(db)  # Вызываем функцию get_top_energies для получения данных
    return results  # Возвращаем результаты в формате JSON

@router.get("/top/brands/", response_model=List[schemas.BrandTop])
def get_top_brands(db: Session = Depends(get_db)):
    return crud.get_top_brands(db)

# ========================= RATINGS =========================
@router.get("/ratings/{rating_id}", response_model=schemas.Rating)
def read_rating(rating_id: int, db: Session = Depends(get_db)):
    db_rating = crud.get_rating(db, rating_id=rating_id)
    if not db_rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return db_rating

@router.get("/reviews/{review_id}/ratings/", response_model=List[schemas.Rating])
def read_review_ratings(review_id: int, db: Session = Depends(get_db)):
    return crud.get_ratings_by_review(db, review_id=review_id)
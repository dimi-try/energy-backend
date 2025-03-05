from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal

router = APIRouter()


# ===================== ФУНКЦИЯ ПОЛУЧЕНИЯ СЕССИИ БД =====================
def get_db():
    """ Создает и закрывает сессию базы данных для каждого запроса """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========================= BRAND ENDPOINTS =========================

@router.get("/brands/", response_model=list[schemas.Brand])
def read_brands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """ Получить список всех брендов энергетиков """
    return crud.get_brands(db, skip=skip, limit=limit)


@router.get("/brands/{brand_id}", response_model=schemas.Brand)
def read_brand(brand_id: int, db: Session = Depends(get_db)):
    """ Получить информацию о конкретном бренде по ID """
    db_brand = crud.get_brand(db, brand_id=brand_id)
    if db_brand is None:
        raise HTTPException(status_code=404, detail="Бренд не найден")
    return db_brand


# ========================= ENERGY ENDPOINTS =========================

@router.get("/energy/", response_model=list[schemas.Energy])
def read_energies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """ Получить список всех энергетиков """
    return crud.get_energies(db, skip=skip, limit=limit)


@router.get("/energy/{energy_id}", response_model=schemas.Energy)
def read_energy(energy_id: int, db: Session = Depends(get_db)):
    """ Получить информацию о конкретном энергетике по ID """
    db_energy = crud.get_energy(db, energy_id=energy_id)
    if db_energy is None:
        raise HTTPException(status_code=404, detail="Энергетик не найден")
    return db_energy


@router.get("/brands/{brand_id}/energy/", response_model=list[schemas.Energy])
def read_energies_by_brand(brand_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """ Получить список энергетиков определенного бренда """
    return crud.get_energies_by_brand(db, brand_id=brand_id, skip=skip, limit=limit)


# ========================= USER ENDPOINTS =========================

@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """ Получить информацию о пользователе по ID """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return db_user


# ========================= RATINGS ENDPOINTS =========================

@router.post("/ratings/", response_model=schemas.Rating)
def create_rating(rating: schemas.RatingCreate, db: Session = Depends(get_db)):
    """ Оставить отзыв и оценку на энергетик """
    return crud.create_rating(db=db, rating=rating)


@router.get("/ratings/{energy_id}", response_model=list[schemas.Rating])
def read_ratings(energy_id: int, db: Session = Depends(get_db)):
    """ Получить все оценки и отзывы по конкретному энергетику """
    return crud.get_ratings_by_energy(db, energy_id=energy_id)


# ========================= USER PROFILE =========================

@router.get("/users/{user_id}/profile", response_model=schemas.UserProfile)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """ Получить профиль пользователя с его статистикой """
    profile = crud.get_user_profile(db, user_id=user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Профиль не найден")
    return profile


# ========================= ТОПЫ =========================

@router.get("/top/energy/", response_model=list[schemas.EnergyTop])
def get_top_energies(db: Session = Depends(get_db)):
    """ Получить топ энергетиков по среднему рейтингу """
    return crud.get_top_energies(db)


@router.get("/top/brands/", response_model=list[schemas.BrandTop])
def get_top_brands(db: Session = Depends(get_db)):
    """ Получить топ брендов энергетиков по среднему рейтингу """
    return crud.get_top_brands(db)

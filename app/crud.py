from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from . import models, schemas
from typing import Dict, Any

# ========================= BRANDS =========================
def get_brand(db: Session, brand_id: int):
    return db.query(models.Brand).filter(models.Brand.id == brand_id).first()

def get_brands(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Brand).offset(skip).limit(limit).all()

# ========================= ENERGIES =========================
def get_energy(db: Session, energy_id: int):
    return db.query(models.Energy).filter(models.Energy.id == energy_id).first()

def get_energies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Energy).offset(skip).limit(limit).all()

def get_energies_by_brand(db: Session, brand_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Energy).filter(models.Energy.brand_id == brand_id).offset(skip).limit(limit).all()

# ========================= USERS =========================
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=user.password  # В реальном приложении необходимо хеширование!
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ========================= REVIEWS & RATINGS =========================
def create_review_with_ratings(db: Session, review: schemas.ReviewCreate):
    # Создаем отзыв
    db_review = models.Review(
        user_id=review.user_id,
        energy_id=review.energy_id,
        review_text=review.review_text
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    # Создаем оценки по критериям
    for rating in review.ratings:
        db_rating = models.Rating(
            review_id=db_review.id,
            criteria_id=rating.criteria_id,
            rating_value=rating.rating_value
        )
        db.add(db_rating)
    
    db.commit()
    return db_review

def get_review(db: Session, review_id: int):
    return db.query(models.Review).filter(models.Review.id == review_id).first()

def get_reviews_by_energy(db: Session, energy_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Review).filter(models.Review.energy_id == energy_id).offset(skip).limit(limit).all()

def get_rating(db: Session, rating_id: int):
    return db.query(models.Rating).filter(models.Rating.id == rating_id).first()

def get_ratings_by_review(db: Session, review_id: int):
    return db.query(models.Rating).filter(models.Rating.review_id == review_id).all()

# ========================= CRITERIA =========================
def create_criteria(db: Session, criteria: schemas.CriteriaCreate):
    db_criteria = models.Criteria(name=criteria.name)
    db.add(db_criteria)
    db.commit()
    db.refresh(db_criteria)
    return db_criteria

def get_criteria_by_name(db: Session, name: str):
    return db.query(models.Criteria).filter(models.Criteria.name == name).first()

def get_all_criteria(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Criteria).offset(skip).limit(limit).all()

# ========================= CATEGORIES =========================
def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_category_by_name(db: Session, name: str):
    return db.query(models.Category).filter(models.Category.name == name).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()

# ========================= USER PROFILE =========================
def get_user_profile(db: Session, user_id: int) -> Dict[str, Any]:
    user = db.query(models.User).get(user_id)
    if not user:
        return None

    # Статистика по оценкам
    reviews = db.query(models.Review).filter(models.Review.user_id == user_id).all()
    total_rated = len(reviews)
    
    if total_rated == 0:
        return {
            "user": user,
            "total_ratings": 0,
            "average_rating": None,
            "favorite_brand": None,
            "favorite_energy": None
        }

    # Расчет среднего рейтинга
    total_rating = 0
    brand_stats = {}
    energy_stats = {}

    for review in reviews:
        ratings = db.query(models.Rating).filter(models.Rating.review_id == review.id).all()
        for rating in ratings:
            total_rating += rating.rating_value
            
            # Статистика по брендам
            energy = db.query(models.Energy).get(review.energy_id)
            brand_id = energy.brand_id
            brand_stats[brand_id] = brand_stats.get(brand_id, 0) + rating.rating_value
            
            # Статистика по энергетикам
            energy_stats[review.energy_id] = energy_stats.get(review.energy_id, 0) + rating.rating_value

    average_rating = total_rating / (total_rated * len(db.query(models.Criteria).all()))

    # Любимый бренд
    favorite_brand_id = max(brand_stats, key=brand_stats.get) if brand_stats else None
    favorite_brand = db.query(models.Brand).get(favorite_brand_id) if favorite_brand_id else None

    # Любимый энергетик
    favorite_energy_id = max(energy_stats, key=energy_stats.get) if energy_stats else None
    favorite_energy = db.query(models.Energy).get(favorite_energy_id) if favorite_energy_id else None

    return {
        "user": user,
        "total_ratings": total_rated,
        "average_rating": round(average_rating, 1),
        "favorite_brand": favorite_brand,
        "favorite_energy": favorite_energy
    }

# ========================= TOP RATINGS =========================
def get_top_energies(db: Session, limit: int = 100):
    subquery = (
        db.query(
            models.Review.energy_id,
        func.round(func.avg(models.Rating.rating_value), 4).label('avg_rating')  # Округление до 4 знаков
        )
        .join(models.Rating)
        .group_by(models.Review.energy_id)
        .subquery()
    )

    return (
        db.query(
            models.Energy,
            func.coalesce(subquery.c.avg_rating, 0).label('average_rating')
        )
        .outerjoin(subquery, models.Energy.id == subquery.c.energy_id)
        .order_by(desc('average_rating'))
        .limit(limit)
        .all()
    )

def get_top_brands(db: Session, limit: int = 100):
    return db.query(
        models.Brand.id,
        models.Brand.name,
        func.round(func.avg(models.Rating.rating_value), 4).label('average_rating')
    ).select_from(models.Brand)\
     .join(models.Energy, models.Brand.id == models.Energy.brand_id)\
     .join(models.Review, models.Energy.id == models.Review.energy_id)\
     .join(models.Rating, models.Review.id == models.Rating.review_id)\
     .group_by(models.Brand.id)\
     .order_by(desc('average_rating'))\
     .limit(limit)\
     .all()
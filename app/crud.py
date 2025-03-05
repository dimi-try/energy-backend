from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from . import models, schemas

# ===================== CRUD ОПЕРАЦИИ С ТАБЛИЦЕЙ BRAND =====================

def get_brand(db: Session, brand_id: int):
    """ Получить бренд по его ID """
    return db.query(models.Brand).filter(models.Brand.id == brand_id).first()


def get_brands(db: Session, skip: int = 0, limit: int = 100):
    """ Получить список всех брендов с пагинацией """
    return db.query(models.Brand).offset(skip).limit(limit).all()


# ===================== CRUD ОПЕРАЦИИ С ТАБЛИЦЕЙ ENERGY =====================

def get_energy(db: Session, energy_id: int):
    """ Получить энергетик по его ID """
    return db.query(models.Energy).filter(models.Energy.id == energy_id).first()


def get_energies(db: Session, skip: int = 0, limit: int = 100):
    """ Получить список всех энергетиков с пагинацией """
    return db.query(models.Energy).offset(skip).limit(limit).all()


def get_energies_by_brand(db: Session, brand_id: int, skip: int = 0, limit: int = 100):
    """ Получить список энергетиков определенного бренда """
    return db.query(models.Energy).filter(models.Energy.brand_id == brand_id).offset(skip).limit(limit).all()


# ===================== CRUD ОПЕРАЦИИ С ТАБЛИЦЕЙ USER =====================

def get_user(db: Session, user_id: int):
    """ Получить пользователя по его ID """
    return db.query(models.User).filter(models.User.id == user_id).first()


# ===================== CRUD ОПЕРАЦИИ С ТАБЛИЦЕЙ RATING =====================

def create_rating(db: Session, rating: schemas.RatingCreate):
    """ Добавить отзыв и оценку на энергетик """
    db_rating = models.Rating(
        user_id=rating.user_id,
        energy_id=rating.energy_id,
        taste_score=rating.taste_score,
        price_score=rating.price_score,
        comment=rating.comment
    )
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating


def get_ratings_by_energy(db: Session, energy_id: int):
    """ Получить все отзывы на конкретный энергетик """
    return db.query(models.Rating).filter(models.Rating.energy_id == energy_id).all()


# ===================== ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ =====================

def get_user_profile(db: Session, user_id: int):
    """ Получить статистику пользователя """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None

    # Получаем оценки пользователя
    ratings = db.query(models.Rating).filter(models.Rating.user_id == user_id).all()
    if not ratings:
        return {
            "user_id": user.id,
            "rated_count": 0,
            "average_score": None,
            "favorite_brand": None,
            "favorite_energy": None
        }

    # Считаем средний балл
    avg_score = sum((r.taste_score + r.price_score) / 2 for r in ratings) / len(ratings)

    # Определяем любимый бренд
    brand_scores = {}
    for r in ratings:
        energy = db.query(models.Energy).filter(models.Energy.id == r.energy_id).first()
        if energy:
            brand_scores[energy.brand_id] = brand_scores.get(energy.brand_id, 0) + ((r.taste_score + r.price_score) / 2)

    favorite_brand = max(brand_scores, key=brand_scores.get) if brand_scores else None

    # Определяем любимый энергетик
    energy_scores = {r.energy_id: (r.taste_score + r.price_score) / 2 for r in ratings}
    favorite_energy = max(energy_scores, key=energy_scores.get) if energy_scores else None

    return {
        "user_id": user.id,
        "rated_count": len(ratings),
        "average_score": avg_score,
        "favorite_brand": favorite_brand,
        "favorite_energy": favorite_energy
    }


# ===================== ТОПЫ =====================

def get_top_energies(db: Session):
    """ Получить топ энергетиков по среднему рейтингу """
    return db.query(
        models.Energy.id,
        models.Energy.name,
        func.avg((models.Rating.taste_score + models.Rating.price_score) / 2).label("average_rating")
    ).join(models.Rating, models.Energy.id == models.Rating.energy_id) \
        .group_by(models.Energy.id) \
        .order_by(func.avg((models.Rating.taste_score + models.Rating.price_score) / 2).desc()) \
        .limit(10).all()


def get_top_brands(db: Session):
    """ Получить топ брендов энергетиков по среднему рейтингу """
    return db.query(
        models.Brand.id,
        models.Brand.name,
        func.avg((models.Rating.taste_score + models.Rating.price_score) / 2).label("average_rating")
    ).join(models.Energy, models.Brand.id == models.Energy.brand_id) \
        .join(models.Rating, models.Energy.id == models.Rating.energy_id) \
        .group_by(models.Brand.id) \
        .order_by(func.avg((models.Rating.taste_score + models.Rating.price_score) / 2).desc()) \
        .limit(10).all()

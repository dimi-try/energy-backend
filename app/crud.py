from sqlalchemy.orm import Session
from sqlalchemy import func, desc, distinct
from . import models, schemas
from typing import Dict, Any

# ========================= BRANDS =========================
def get_brand(db: Session, brand_id: int):
    """
    - Средний рейтинг = среднее от средних оценок энергетиков
    - Только энергетики с оценками учитываются в расчете
    """
    
    # Тот же подзапрос, что и в get_top_brands
    energy_avg_subquery = (
        db.query(
            models.Energy.brand_id,
            func.avg(models.Rating.rating_value).label("energy_avg_rating")
        )
        .join(models.Review, models.Energy.id == models.Review.energy_id)
        .join(models.Rating, models.Review.id == models.Rating.review_id)
        .group_by(models.Energy.id)
        .subquery()
    )

    result = (
        db.query(
            models.Brand,
            # Среднее от средних оценок энергетиков (как в get_top_brands)
            func.round(func.avg(energy_avg_subquery.c.energy_avg_rating), 4).label("average_rating"),
            # Общее количество энергетиков
            func.count(distinct(models.Energy.id)).label("energy_count"),
            # Количество энергетиков с оценками
            func.count(distinct(energy_avg_subquery.c.energy_avg_rating)).label("rated_energy_count"),
            # Общее количество отзывов
            func.count(distinct(models.Review.id)).label("review_count"),
            # Общее количество оценок
            func.count(distinct(models.Rating.id)).label("rating_count"),
        )
        .outerjoin(models.Energy, models.Brand.id == models.Energy.brand_id)
        .outerjoin(energy_avg_subquery, models.Brand.id == energy_avg_subquery.c.brand_id)
        .outerjoin(models.Review, models.Energy.id == models.Review.energy_id)
        .outerjoin(models.Rating, models.Review.id == models.Rating.review_id)
        .filter(models.Brand.id == brand_id)
        .group_by(models.Brand.id)
        .first()
    )

    if result:
        brand, avg_rating, energy_count, rated_energy_count, review_count, rating_count = result
        
        # Полная синхронизация логики с get_top_brands
        final_rating = round(float(avg_rating), 4) if avg_rating and rated_energy_count > 0 else 0.0
        
        # Добавляем вычисленные поля в объект бренда
        brand.average_rating = final_rating
        brand.energy_count = energy_count or 0
        brand.rated_energy_count = rated_energy_count or 0
        brand.review_count = review_count or 0
        brand.rating_count = rating_count or 0
        
        return brand
    return None

def get_brands(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Brand).offset(skip).limit(limit).all()

# ========================= ENERGIES =========================
def get_energy(db: Session, energy_id: int):
    result = db.query(
        models.Energy,
        func.coalesce(func.round(func.avg(models.Rating.rating_value), 4).label('average_rating'))
    ).outerjoin(models.Review, models.Energy.id == models.Review.energy_id)\
     .outerjoin(models.Rating, models.Review.id == models.Rating.review_id)\
     .filter(models.Energy.id == energy_id)\
     .group_by(models.Energy.id)\
     .first()

    if result:
        energy, avg_rating = result
        energy.average_rating = float(avg_rating) if avg_rating else 0.0
        return energy
    return None



def get_energies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Energy).offset(skip).limit(limit).all()

def get_energies_by_brand(db: Session, brand_id: int, skip: int = 0, limit: int = 100):
    """
    Получает все энергетики бренда с:
    - Средним рейтингом
    - Количеством отзывов
    - Сортировкой по рейтингу
    """
    results = (
        db.query(
            models.Energy,
            # Средний рейтинг энергетика
            func.coalesce(func.round(func.avg(models.Rating.rating_value), 4), 0).label("average_rating"),
            # Количество отзывов для энергетика
            func.count(distinct(models.Review.id)).label("review_count"),
        )
        .filter(models.Energy.brand_id == brand_id)
        .outerjoin(models.Review, models.Energy.id == models.Review.energy_id)
        .outerjoin(models.Rating, models.Review.id == models.Rating.review_id)
        .group_by(models.Energy.id)
        .order_by(desc("average_rating"))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        {
            **energy.__dict__,
            "average_rating": float(average_rating),
            "review_count": review_count,
            "brand": energy.brand,
            "category": energy.category,
        }
        for energy, average_rating, review_count in results
    ]

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

# проверка на то был ли отзыв написан юзером или нет
def get_review_by_user_and_energy(db: Session, user_id: int, energy_id: int):
    return db.query(models.Review).filter(
        models.Review.user_id == user_id,
        models.Review.energy_id == energy_id
    ).first()

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
    # Подзапрос для вычисления среднего рейтинга для каждого energy_id
    avg_rating_subquery = (
        db.query(
            models.Review.energy_id,  # Выбираем energy_id из таблицы Review
            func.round(func.avg(models.Rating.rating_value), 4).label('avg_rating')  # Средний рейтинг с округлением до 4 знаков
        )
        .join(models.Rating)  # Присоединяем таблицу Rating к Review для получения рейтингов
        .group_by(models.Review.energy_id)  # Группируем результаты по energy_id
        .subquery()  # Преобразуем запрос в подзапрос для использования в основном запросе
    )

    # Подзапрос для вычисления количества отзывов для каждого energy_id
    review_count_subquery = (
        db.query(
            models.Review.energy_id,  # Выбираем energy_id из таблицы Review
            func.count(models.Review.id).label('review_count')  # Количество отзывов для каждого energy_id
        )
        .group_by(models.Review.energy_id)  # Группируем результаты по energy_id
        .subquery()  # Преобразуем запрос в подзапрос для использования в основном запросе
    )

    # Основной запрос для получения топ energy с их средним рейтингом и количеством отзывов
    energies = (
        db.query(
            models.Energy,  # Выбираем все поля из таблицы Energy
            func.coalesce(avg_rating_subquery.c.avg_rating, 0).label('average_rating'),  # Используем средний рейтинг из подзапроса или 0, если рейтинга нет
            func.coalesce(review_count_subquery.c.review_count, 0).label('review_count')  # Используем количество отзывов из подзапроса или 0, если отзывов нет
        )
        .outerjoin(avg_rating_subquery, models.Energy.id == avg_rating_subquery.c.energy_id)  # Присоединяем подзапрос со средним рейтингом
        .outerjoin(review_count_subquery, models.Energy.id == review_count_subquery.c.energy_id)  # Присоединяем подзапрос с количеством отзывов
        .join(models.Brand)  # Явно присоединяем таблицу Brand для сортировки по бренду
        .order_by(
            desc('average_rating'),  # Сортируем по убыванию среднего рейтинга
            desc('review_count'),  # Затем по убыванию количества отзывов
            models.Brand.name,  # Затем по названию бренда (по возрастанию)
            models.Energy.name  # Затем по названию энергетика (по возрастанию)
        )
        .limit(limit)  # Ограничиваем количество результатов значением limit
        .all()  # Выполняем запрос и получаем все результаты
    )

    # Возвращаем список energy с добавленным average_rating и review_count
    return [{
        "id": energy.id,  # ID энергетика
        "name": energy.name,  # Название энергетика
        "average_rating": float(avg_rating),  # Средний рейтинг энергетика (приводим к float для condecimal)
        "brand": energy.brand,  # Бренд энергетика (должен быть объектом модели Brand)
        "category": energy.category,  # Категория энергетика (должен быть объектом модели Category или None)
        "review_count": review_count  # Количество отзывов для данного энергетика
    } for energy, avg_rating, review_count in energies]  # Проходим по каждому результату и формируем словарь

def get_top_brands(db: Session, limit: int = 100):
    """
    Получает топ брендов с:
    - Средним рейтингом (правильный расчет)
    - Количеством энергетиков
    - Количеством отзывов
    - Количеством оценок
    - Сортировкой по рейтингу
    """
    # Подзапрос для средних рейтингов энергетиков
    energy_avg_subquery = (
        db.query(
            models.Energy.brand_id,
            func.avg(models.Rating.rating_value).label("energy_avg_rating"),
        )
        .outerjoin(models.Review, models.Energy.id == models.Review.energy_id)
        .outerjoin(models.Rating, models.Review.id == models.Rating.review_id)
        .group_by(models.Energy.id)
        .subquery()
    )

    results = (
        db.query(
            models.Brand.id,
            models.Brand.name,
            # Средний рейтинг бренда
            func.coalesce(func.round(func.avg(energy_avg_subquery.c.energy_avg_rating), 4), 0).label("average_rating"),
            # Количество энергетиков
            func.count(distinct(models.Energy.id)).label("energy_count"),
            # Количество отзывов
            func.count(distinct(models.Review.id)).label("review_count"),
            # Количество оценок
            func.count(distinct(models.Rating.id)).label("rating_count"),
        )
        .outerjoin(models.Energy, models.Brand.id == models.Energy.brand_id)
        .outerjoin(energy_avg_subquery, models.Brand.id == energy_avg_subquery.c.brand_id)
        .outerjoin(models.Review, models.Energy.id == models.Review.energy_id)
        .outerjoin(models.Rating, models.Review.id == models.Rating.review_id)
        .group_by(models.Brand.id)
        .order_by(desc("average_rating"))
        .limit(limit)
        .all()
    )

    return [
        {
            "id": brand_id,
            "name": name,
            "average_rating": float(average_rating),
            "energy_count": energy_count,
            "review_count": review_count,
            "rating_count": rating_count,
        }
        for brand_id, name, average_rating, energy_count, review_count, rating_count in results
    ]
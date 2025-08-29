from sqlalchemy.orm import Session
from typing import Dict, Any
from sqlalchemy.exc import DataError
from fastapi import HTTPException

from app.core.config import TG_ADMIN_IDS

from app.db.models import User, Review, Rating, Energy, Brand, Criteria, Role, UserRole

from app.schemas.users import User as UserSchema, UserCreate, UserUpdate

# =============== CREATE ===============
def create_user(db: Session, user: UserCreate, telegram_id: int):
    try:
        # Создаём новый объект User
        db_user = User(
            id=telegram_id,  # Устанавливаем telegram_id как id
            username=user.username,
            image_url=user.image_url
        )
        # Добавляем объект в сессию
        db.add(db_user)
        # Назначаем роль
        role_name = "admin" if str(telegram_id) in TG_ADMIN_IDS else "user"
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            raise ValueError(f"Role {role_name} not found in database")
        user_role = UserRole(user_id=telegram_id, role_id=role.id)
        db.add(user_role)
        # Фиксируем изменения
        db.commit()
        # Обновляем объект
        db.refresh(db_user)
        # Возвращаем пользователя
        return db_user
    except DataError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid telegram_id: {str(e)}")

# =============== READ ONE ===============
def get_user(db: Session, user_id: int):
    # Выполняем запрос к таблице User
    query = db.query(User)
    # Фильтруем по user_id
    query = query.filter(User.id == user_id)
    # Получаем первый результат
    return query.first()

# =============== UPDATE ===============
def update_user(db: Session, user_id: int, user_update: UserUpdate):
    # Получаем пользователя по ID
    db_user = db.query(User).get(user_id)
    if not db_user:
        return None
    # Обновляем username, если он предоставлен
    if user_update.username:
        db_user.username = user_update.username
    # Обновляем фото, если оно предоставлено
    if user_update.image_url:
        db_user.image_url = user_update.image_url
    # Фиксируем изменения
    db.commit()
    # Обновляем объект
    db.refresh(db_user)
    return db_user

# =============== READ ONE PROFILE ===============
def get_user_profile(db: Session, user_id: int) -> Dict[str, Any]:
    # Получаем пользователя по ID
    user = db.query(User).get(user_id)
    # Проверяем, существует ли пользователь
    if not user:
        # Возвращаем None, если пользователь не найден
        return None

    # Получаем отзывы пользователя
    reviews = db.query(Review).filter(Review.user_id == user_id).all()
    # Считаем количество отзывов
    total_rated = len(reviews)
    
    # Проверяем наличие отзывов
    if total_rated == 0:
        # Возвращаем базовый профиль без статистики
        return {
            "user": user,
            "total_ratings": 0,
            "average_rating": None,
            "favorite_brand": None,
            "favorite_energy": None
        }

    # Инициализируем переменные
    total_rating = 0
    # Создаём словарь для брендов
    brand_stats = {}
    # Создаём словарь для энергетиков
    energy_stats = {}

    # Проходим по отзывам
    for review in reviews:
        # Получаем оценки для отзыва
        ratings = db.query(Rating).filter(Rating.review_id == review.id).all()
        # Проходим по оценкам
        for rating in ratings:
            # Добавляем оценку к общей сумме
            total_rating += rating.rating_value
            # Получаем энергетик
            energy = db.query(Energy).get(review.energy_id)
            # Получаем ID бренда
            brand_id = energy.brand_id
            # Добавляем оценку в статистику бренда
            brand_stats[brand_id] = brand_stats.get(brand_id, 0) + rating.rating_value
            # Добавляем оценку в статистику энергетика
            energy_stats[review.energy_id] = energy_stats.get(review.energy_id, 0) + rating.rating_value

    # Вычисляем средний рейтинг
    average_rating = total_rating / (total_rated * len(db.query(Criteria).all()))

    # Определяем любимый бренд
    favorite_brand_id = max(brand_stats, key=brand_stats.get) if brand_stats else None
    # Получаем бренд
    favorite_brand = db.query(Brand).get(favorite_brand_id) if favorite_brand_id else None

    # Определяем любимый энергетик
    favorite_energy_id = max(energy_stats, key=energy_stats.get) if energy_stats else None
    # Получаем энергетик
    favorite_energy = db.query(Energy).get(favorite_energy_id) if favorite_energy_id else None

    # Возвращаем профиль со статистикой
    return {
        "user": user,
        "total_ratings": total_rated,
        "average_rating": round(average_rating, 1),
        "favorite_brand": favorite_brand,
        "favorite_energy": favorite_energy
    }

# =============== READ ALL REVIEWS ONE USER===============
def get_user_reviews(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    # Проверяем существование пользователя
    user = db.query(User).get(user_id)
    if not user:
        return None
    # Выполняем запрос с присоединением таблиц
    reviews = (
        db.query(Review)
        .filter(Review.user_id == user_id)
        .join(Energy, Review.energy_id == Energy.id)
        .join(Brand, Energy.brand_id == Brand.id)
        .order_by(Review.created_at.desc())  # сортировка по убыванию (сначала новые)
        .offset(skip)
        .limit(limit)
        .all()
    )
    # Формируем результат
    result = []
    for review in reviews:
        # Получаем энергетик
        energy = db.query(Energy).get(review.energy_id)
        # Получаем бренд
        brand = db.query(Brand).get(energy.brand_id)
        # Получаем оценки
        ratings = db.query(Rating).filter(Rating.review_id == review.id).all()
        # Добавляем данные в результат
        review_dict = review.__dict__
        review_dict["energy"] = energy.name  # Добавляем только имя энергетика
        review_dict["brand"] = brand.name  # Добавляем только имя бренда
        review_dict["ratings"] = ratings
        review_dict["average_rating_review"] = (
            round(sum(rating.rating_value for rating in ratings) / len(ratings), 4) if ratings else 0.0
        )
        result.append(review_dict)
    # Возвращаем результат
    return {"reviews": result}

# =============== READ TOTAL REVIEWS COUNT ===============
def get_total_reviews(db: Session, user_id: int):
    """
    Возвращает общее количество отзывов пользователя.
    """
    return db.query(Review).filter(Review.user_id == user_id).count()

# =============== READ ALREADY REVIEW BY USER ===============
def get_review_by_user_and_energy(db: Session, user_id: int, energy_id: int):
    # Выполняем запрос к таблице Review
    query = db.query(Review)
    # Фильтруем по user_id и energy_id
    query = query.filter(
        Review.user_id == user_id,
        Review.energy_id == energy_id
    )
    # Получаем первый результат
    return query.first()
    
# =============== ONLY ADMINS ===============

# =============== READ ALL ===============
def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Получает список всех пользователей с пагинацией.
    """
    query = db.query(User)
    query = query.offset(skip)
    query = query.limit(limit)
    return query.all()

# =============== DELETE ===============
def delete_user(db: Session, user_id: int):
    """
    Удаляет пользователя по его ID.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return False
    # Удаляем связанные записи в таблице user_roles
    db.query(UserRole).filter(UserRole.user_id == user_id).delete()
    # Удаляем фото
    if db_user.image_url and os.path.exists(db_user.image_url):
        os.remove(db_user.image_url)
    # Удаляем пользователя
    db.delete(db_user)
    db.commit()
    return True
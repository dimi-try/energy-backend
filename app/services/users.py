# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем Dict и Any из typing для аннотации
from typing import Dict, Any
# Импортируем модели
from app.db.models import User, Review, Rating, Energy, Brand, Criteria
# Импортируем схемы
from app.schemas.user import User as UserSchema, UserCreate

# Определяем функцию для получения пользователя по ID
def get_user(db: Session, user_id: int):
    # Выполняем запрос к таблице User
    query = db.query(User)
    # Фильтруем по user_id
    query = query.filter(User.id == user_id)
    # Получаем первый результат
    return query.first()

# Определяем функцию для получения пользователя по email
def get_user_by_email(db: Session, email: str):
    # Выполняем запрос к таблице User
    query = db.query(User)
    # Фильтруем по email
    query = query.filter(User.email == email)
    # Получаем первый результат
    return query.first()

# Определяем функцию для создания пользователя
def create_user(db: Session, user: UserCreate):
    # Создаём новый объект User
    db_user = User(
        # Устанавливаем имя пользователя
        username=user.username,
        # Устанавливаем email
        email=user.email,
        # Устанавливаем пароль (без хеширования)
        password=user.password  # В реальном приложении добавить хеширование!
    )
    # Добавляем объект в сессию
    db.add(db_user)
    # Фиксируем изменения
    db.commit()
    # Обновляем объект
    db.refresh(db_user)
    # Возвращаем пользователя
    return db_user

# Определяем функцию для проверки отзыва пользователя
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

# Определяем функцию для получения профиля пользователя
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

# Определяем функцию для получения отзывов пользователя
def get_user_reviews(db: Session, user_id: int, skip: int = 0, limit: int = 100):
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


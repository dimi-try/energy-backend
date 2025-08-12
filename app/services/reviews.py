# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем функции SQLAlchemy для агрегации и сортировки
from sqlalchemy import func, desc, distinct
# Импортируем модели
from app.db.models import Review, Rating, Energy, Brand, User
# Импортируем схемы 
from app.schemas.reviews import ReviewCreate, ReviewUpdate

# Определяем функцию для создания отзыва с оценками
def create_review_with_ratings(db: Session, review: ReviewCreate):
    # Создаём объект Review
    db_review = Review(
        # Устанавливаем ID пользователя
        user_id=review.user_id,
        # Устанавливаем ID энергетика
        energy_id=review.energy_id,
        # Устанавливаем текст отзыва
        review_text=review.review_text
    )
    # Добавляем отзыв в сессию
    db.add(db_review)
    # Фиксируем изменения
    db.commit()
    # Обновляем объект
    db.refresh(db_review)
    
    # Проходим по оценкам
    for rating in review.ratings:
        # Создаём объект Rating
        db_rating = Rating(
            # Устанавливаем ID отзыва
            review_id=db_review.id,
            # Устанавливаем ID критерия
            criteria_id=rating.criteria_id,
            # Устанавливаем значение оценки
            rating_value=rating.rating_value
        )
        # Добавляем оценку в сессию
        db.add(db_rating)
    
    # Фиксируем изменения
    db.commit()
    # Возвращаем отзыв
    return db_review

# Определяем функцию для получения отзыва по ID
def get_review(db: Session, review_id: int):
    # Выполняем запрос к таблице Review
    query = db.query(Review)
    # Фильтруем по review_id
    query = query.filter(Review.id == review_id)
    # Получаем первый результат
    return query.first()

# Определяем функцию для получения всех отзывов
def get_all_reviews(db: Session, skip: int = 0, limit: int = 100):
    """
    Получает список всех отзывов с пагинацией.
    """
    query = (
        db.query(Review)
        .join(Energy, Review.energy_id == Energy.id)
        .join(User, Review.user_id == User.id)
        .order_by(Review.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = query.all()
    for review in result:
        avg_rating = (
            db.query(func.avg(Rating.rating_value))
            .filter(Rating.review_id == review.id)
            .scalar()
        )
        review.average_rating_review = round(float(avg_rating), 4) if avg_rating else 0.0
    return result

# Определяем функцию для обновления отзыва
def update_review(db: Session, review_id: int, review_update: ReviewUpdate):
    # Получаем отзыв по ID
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if not db_review:
        return None
    # Обновляем текст отзыва, если предоставлен
    if review_update.review_text is not None:
        db_review.review_text = review_update.review_text
    # Обновляем оценки, если предоставлены
    if review_update.ratings:
        # Удаляем существующие оценки
        db.query(Rating).filter(Rating.review_id == review_id).delete()
        # Добавляем новые оценки
        for rating in review_update.ratings:
            db_rating = Rating(
                review_id=review_id,
                criteria_id=rating.criteria_id,
                rating_value=rating.rating_value
            )
            db.add(db_rating)
    # Фиксируем изменения
    db.commit()
    # Обновляем объект
    db.refresh(db_review)
    # Вычисляем средний рейтинг
    avg_rating = (
        db.query(func.avg(Rating.rating_value))
        .filter(Rating.review_id == db_review.id)
        .scalar()
    )
    db_review.average_rating_review = round(float(avg_rating), 4) if avg_rating else 0.0
    return db_review

# Определяем функцию для удаления отзыва
def delete_review(db: Session, review_id: int):
    # Получаем отзыв по ID
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if not db_review:
        return False
    # Удаляем связанные оценки
    db.query(Rating).filter(Rating.review_id == review_id).delete()
    # Удаляем отзыв
    db.delete(db_review)
    # Фиксируем изменения
    db.commit()
    return True

# Определяем функцию для получения отзывов на энергетик
def get_reviews_by_energy(db: Session, energy_id: int, skip: int = 0, limit: int = 100):
    # Выполняем запрос к таблице Review с фильтрацией и сортировкой
    query = (
        db.query(Review) # Выполняем запрос к таблице Review
        .filter(Review.energy_id == energy_id) # Фильтруем по energy_id
        .order_by(Review.created_at.desc())  # сортировка по убыванию (сначала новые)
        .offset(skip) # Применяем смещение
        .limit(limit) # Ограничиваем записи
    )

    # Получаем все результаты
    result = query.all()

    # Проверяем, есть ли результаты
    if not result:
        return []  
    # Добавляем средний рейтинг к каждому отзыву
    for review in result:   
        # Выполняем запрос к таблице Rating для получения среднего рейтинга
        avg_rating = (
            db.query(func.avg(Rating.rating_value))
            .filter(Rating.review_id == review.id)
            .scalar()
        )
        # Устанавливаем средний рейтинг в отзыв
        review.average_rating_review = round(float(avg_rating), 4) if avg_rating else 0.0
    # Возвращаем список отзывов с установленным средним рейтингом
    return result
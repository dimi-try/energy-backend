from sqlalchemy.orm import Session
from sqlalchemy import func, desc, distinct
import os

from app.db.models import Review, Rating, Energy, Brand, User

from app.schemas.reviews import ReviewCreate, ReviewUpdate

# =============== CREATE ===============
def create_review_with_ratings(db: Session, review: ReviewCreate):
    # Создаём объект Review
    db_review = Review(
        # Устанавливаем ID пользователя
        user_id=review.user_id,
        # Устанавливаем ID энергетика
        energy_id=review.energy_id,
        # Устанавливаем текст отзыва
        review_text=review.review_text,
        # Устанавливаем URL изображения отзыва,
        image_url=review.image_url            
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

# =============== READ ONE ===============
def get_review(db: Session, review_id: int):
    # Выполняем запрос к таблице Review
    query = db.query(Review)
    # Фильтруем по review_id
    query = query.filter(Review.id == review_id)
    # Получаем первый результат
    return query.first()

# =============== UPDATE ===============
def update_review(db: Session, review_id: int, review_update: ReviewUpdate):
    # Получаем отзыв по ID
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if not db_review:
        return None
    # Обновляем текст отзыва, если предоставлен
    if review_update.review_text is not None:
        db_review.review_text = review_update.review_text
    # Обновляем URL изображения, если предоставлен
    if review_update.image_url is not None:
        if db_review.image_url and os.path.exists(db_review.image_url):
            os.remove(db_review.image_url)  # Удаляем старый файл
        db_review.image_url = review_update.image_url
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

# =============== DELETE ===============
def delete_review(db: Session, review_id: int):
    # Получаем отзыв по ID
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if not db_review:
        return False
    if db_review.image_url and os.path.exists(db_review.image_url):
        os.remove(db_review.image_url)  # Удаляем файл
    # Удаляем связанные оценки
    db.query(Rating).filter(Rating.review_id == review_id).delete()
    # Удаляем отзыв
    db.delete(db_review)
    # Фиксируем изменения
    db.commit()
    return True

# =============== ONLY ADMINS ===============

# =============== READ ALL ===============
def get_all_reviews(db: Session, skip: int = 0, limit: int = 10):
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

# =============== READ TOTAL REVIEWS COUNT FOR ADMIN ===============
def get_total_reviews_admin(db: Session):
    """
    Возвращает общее количество отзывов.
    """
    query = db.query(Review)
    
    return query.count()
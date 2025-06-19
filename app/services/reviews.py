# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем модели
from app.db.models import Review, Rating
# Импортируем схемы 
from app.schemas.review import ReviewCreate

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

# Определяем функцию для получения отзывов на энергетик
def get_reviews_by_energy(db: Session, energy_id: int, skip: int = 0, limit: int = 100):
    # Выполняем запрос к таблице Review
    query = db.query(Review)
    # Фильтруем по energy_id
    query = query.filter(Review.energy_id == energy_id)
    # Применяем смещение
    query = query.offset(skip)
    # Ограничиваем записи
    query = query.limit(limit)
    # Получаем все результаты
    return query.all()


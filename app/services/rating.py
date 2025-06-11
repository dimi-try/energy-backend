# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем модели
from app.db.models import Rating

# Определяем функцию для получения оценки по ID
def get_rating(db: Session, rating_id: int):
    # Выполняем запрос к таблице Rating
    query = db.query(Rating)
    # Фильтруем по rating_id
    query = query.filter(Rating.id == rating_id)
    # Получаем первый результат
    return query.first()

# Определяем функцию для получения оценок отзыва
def get_ratings_by_review(db: Session, review_id: int):
    # Выполняем запрос к таблице Rating
    query = db.query(Rating)
    # Фильтруем по review_id
    query = query.filter(Rating.review_id == review_id)
    # Получаем все результаты
    return query.all()
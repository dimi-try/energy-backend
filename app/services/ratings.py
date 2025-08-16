from sqlalchemy.orm import Session
from app.db.models import Rating

# =============== READ ONE ===============
def get_rating(db: Session, rating_id: int):
    # Выполняем запрос к таблице Rating
    query = db.query(Rating)
    # Фильтруем по rating_id
    query = query.filter(Rating.id == rating_id)
    # Получаем первый результат
    return query.first()

# =============== READ ALL RATINGS ONE REVIEW===============
def get_ratings_by_review(db: Session, review_id: int):
    # Выполняем запрос к таблице Rating
    query = db.query(Rating)
    # Фильтруем по review_id
    query = query.filter(Rating.review_id == review_id)
    # Получаем все результаты
    return query.all()
# Импортируем нужное из SQLAlchemy
from sqlalchemy import Column, Integer, ForeignKey, Numeric
# Импортируем relationship для определения связей
from sqlalchemy.orm import relationship

# Импортируем базовый класс
from app.db.models.base import Base

# Определяем класс модели Rating
class Rating(Base):
    # Указываем имя таблицы
    __tablename__ = "ratings"

    # Определяем поле id как первичный ключ
    id = Column(Integer, primary_key=True, index=True)
    # Определяем поле review_id как внешний ключ
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    # Определяем поле criteria_id как внешний ключ
    criteria_id = Column(Integer, ForeignKey("criteria.id"), nullable=False)
    # Определяем поле rating_value как числовое (3 знака, 1 после запятой)
    rating_value = Column(Numeric(3, 1), nullable=False)
    
    # Определяем связь с отзывом
    review = relationship("Review", back_populates="ratings")
    # Определяем связь с критерием
    criteria = relationship("Criteria", back_populates="ratings")
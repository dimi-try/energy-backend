# Импортируем Column, Integer, ForeignKey, Text, TIMESTAMP из SQLAlchemy
from sqlalchemy import Column, Integer, ForeignKey, Text, TIMESTAMP
# Импортируем relationship для определения связей
from sqlalchemy.orm import relationship
# Импортируем datetime для установки значений по умолчанию
from datetime import datetime
# Импортируем базовый класс
from app.db.models.base import Base

# Определяем класс модели Review
class Review(Base):
    # Указываем имя таблицы
    __tablename__ = "reviews"

    # Определяем поле id как первичный ключ
    id = Column(Integer, primary_key=True, index=True)
    # Определяем поле user_id как внешний ключ
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Определяем поле energy_id как внешний ключ
    energy_id = Column(Integer, ForeignKey("energetics.id"), nullable=False)
    # Определяем поле review_text как текстовое
    review_text = Column(Text, nullable=False)
    # Определяем поле created_at с текущей датой по умолчанию
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Определяем связь с пользователем
    user = relationship("User", back_populates="reviews")
    # Определяем связь с энергетиком
    energy = relationship("Energy", back_populates="reviews")
    # Определяем связь один-ко-многим с оценками
    ratings = relationship("Rating", back_populates="review")
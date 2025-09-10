# Импортируем нужное из SQLAlchemy
from sqlalchemy import Column, Integer, ForeignKey, Text, BigInteger, String
# Импортируем relationship для определения связей
from sqlalchemy.orm import relationship
# Импортируем time для работы с временными метками
import time
# Импортируем базовый класс
from app.db.models.base import Base

# Определяем класс модели Review
class Review(Base):
    # Указываем имя таблицы
    __tablename__ = "reviews"

    # Определяем поле id как первичный ключ
    id = Column(Integer, primary_key=True, index=True)
    # Определяем поле user_id как внешний ключ
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    # Определяем поле energy_id как внешний ключ
    energy_id = Column(Integer, ForeignKey("energetics.id"), nullable=False)
    # Определяем поле review_text как текстовое
    review_text = Column(Text, nullable=True)
    # Определяем поле created_at с текущей датой по умолчанию
    created_at = Column(BigInteger, default=lambda: int(time.time()))  # Unix timestamp в секундах
    # Поле для URL фото
    image_url = Column(String(255), nullable=True)

    # Определяем связь с пользователем
    user = relationship("User", back_populates="reviews")
    # Определяем связь с энергетиком
    energy = relationship("Energy", back_populates="reviews")
    # Определяем связь один-ко-многим с оценками
    ratings = relationship("Rating", back_populates="review", cascade="all, delete-orphan")
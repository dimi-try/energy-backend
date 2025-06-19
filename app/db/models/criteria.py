# Импортируем Column и Integer из SQLAlchemy для определения полей
from sqlalchemy import Column, Integer, String
# Импортируем relationship для определения связей
from sqlalchemy.orm import relationship
# Импортируем базовый класс
from app.db.models.base import Base

# Определяем класс модели Criteria
class Criteria(Base):
    # Указываем имя таблицы
    __tablename__ = "criteria"

    # Определяем поле id как первичный ключ
    id = Column(Integer, primary_key=True, index=True)
    # Определяем поле name как уникальное строковое
    name = Column(String(100), unique=True, nullable=False)

    # Связь: один критерий -> много оценок
    ratings = relationship("Rating", back_populates="criteria")
# Импортируем Column и Integer из SQLAlchemy для определения полей
from sqlalchemy import Column, Integer, String
# Импортируем relationship для определения связей
from sqlalchemy.orm import relationship
# Импортируем базовый класс
from app.db.models.base import Base

# Определяем класс модели Category
class Category(Base):
    # Указываем имя таблицы
    __tablename__ = "categories"

    # Определяем поле id как первичный ключ
    id = Column(Integer, primary_key=True, index=True)
    # Определяем поле name как уникальное строковое
    name = Column(String(100), unique=True, nullable=False)

    # Связь: одна категория -> много энергетиков
    energies = relationship("Energy", back_populates="category")
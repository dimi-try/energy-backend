# Импортируем Column, Integer, String, ForeignKey, Text из SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Text
# Импортируем relationship для определения связей
from sqlalchemy.orm import relationship
# Импортируем базовый класс
from app.db.models.base import Base

# Определяем класс модели Energy
class Energy(Base):
    # Указываем имя таблицы
    __tablename__ = "energetics"

    # Определяем поле id как первичный ключ
    id = Column(Integer, primary_key=True, index=True)
    # Определяем поле name как строковое
    name = Column(String(255), nullable=False)
    # Определяем поле brand_id как внешний ключ
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    # Определяем поле category_id как внешний ключ (может быть пустым)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    # Определяем поле description как текстовое
    description = Column(Text, nullable=True)
    # Определяем поле ingredients как текстовое
    ingredients = Column(Text, nullable=True)
    # Определяем поле image_url как строковое
    image_url = Column(String(255), nullable=True)

    # Определяем связь с брендом
    brand = relationship("Brand", back_populates="energies")
    # Определяем связь с категорией
    category = relationship("Category", back_populates="energies")
    # Определяем связь один-ко-многим с отзывами
    reviews = relationship("Review", back_populates="energy")
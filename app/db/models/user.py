# Импортируем Column, Integer, String, Boolean, TIMESTAMP из SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
# Импортируем relationship для определения связей
from sqlalchemy.orm import relationship
# Импортируем datetime для установки значений по умолчанию
from datetime import datetime
# Импортируем базовый класс
from app.db.models.base import Base

# Определяем класс модели User
class User(Base):
    # Указываем имя таблицы
    __tablename__ = "users"

    # Определяем поле id как первичный ключ
    id = Column(Integer, primary_key=True, index=True)
    # Определяем поле username как уникальное строковое
    username = Column(String(100), unique=True, nullable=False)
    # Определяем поле email как уникальное строковое
    email = Column(String(255), unique=True, nullable=False)
    # Определяем поле password как строковое
    password = Column(String(255), nullable=False)
    # Определяем поле is_premium как булево
    is_premium = Column(Boolean, default=False)
    # Определяем поле created_at с текущей датой по умолчанию
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Определяем связь один-ко-многим с отзывами
    reviews = relationship("Review", back_populates="user")
    # Определяем связь многие-ко-многим с ролями
    roles = relationship("UserRole", back_populates="user")
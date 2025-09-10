# Импортируем нужное SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, BigInteger  # Добавляем BigInteger
# Импортируем relationship для определения связей
from sqlalchemy.orm import relationship
# Импортируем time для работы с временными метками
import time
# Импортируем базовый класс
from app.db.models.base import Base

# Определяем класс модели User
class User(Base):
    # Указываем имя таблицы
    __tablename__ = "users"

    # Определяем поле id как первичный ключ с типом BigInteger
    id = Column(BigInteger, primary_key=True, index=True)
    # Определяем поле username как уникальное строковое
    username = Column(String(100), nullable=False)
    # Определяем поле is_premium как булево
    is_premium = Column(Boolean, default=False)
    # Определяем поле created_at с текущей датой по умолчанию
    created_at = Column(BigInteger, default=lambda: int(time.time()))  # Unix timestamp в секундах
    # Поле для URL фото
    image_url = Column(String(255), nullable=True)

    # Определяем связь один-ко-многим с отзывами
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    # Определяем связь многие-ко-многим с ролями
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    # Определяем связь с черным списком, даже если пользователь еще не зарегистрирован
    blacklist_entry = relationship(
        "Blacklist",
        back_populates="user",
        primaryjoin="User.id==foreign(Blacklist.user_id)",
        uselist=False
    )
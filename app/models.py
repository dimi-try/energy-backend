from sqlalchemy import Column, Integer, String, ForeignKey, Text, Numeric, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


# Таблица брендов энергетиков
class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)  # Уникальный ID бренда
    name = Column(String(255), unique=True, nullable=False)  # Название бренда (уникальное)

    # Связь: один бренд -> много энергетиков
    energies = relationship("Energy", back_populates="brand")


# Таблица категорий энергетиков (например, "Классический", "Предтреник" и т. д.)
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)  # Уникальный ID категории
    name = Column(String(100), unique=True, nullable=False)  # Название категории (уникальное)

    # Связь: одна категория -> много энергетиков
    energies = relationship("Energy", back_populates="category")


# Таблица энергетиков (основная информация о напитках)
class Energy(Base):
    __tablename__ = "energetics"

    id = Column(Integer, primary_key=True, index=True)  # Уникальный ID энергетика
    name = Column(String(255), nullable=False)  # Название энергетика
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)  # Связь с брендом
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)  # Связь с категорией
    description = Column(Text, nullable=True)  # Описание энергетика
    ingredients = Column(Text, nullable=True)  # Ингредиенты
    image_url = Column(String(255), nullable=True)  # Ссылка на изображение

    # Определение связей
    brand = relationship("Brand", back_populates="energies")  # Связь с брендом
    category = relationship("Category", back_populates="energies")  # Связь с категорией
    ratings = relationship("Rating", back_populates="energy")  # Связь с отзывами/оценками


# Таблица пользователей
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # Уникальный ID пользователя
    username = Column(String(100), unique=True, nullable=False)  # Уникальное имя пользователя
    email = Column(String(255), unique=True, nullable=False)  # Уникальная почта пользователя
    password = Column(String(255), nullable=False)  # Пароль (захешированный)
    is_premium = Column(Boolean, default=False)  # Флаг: является ли пользователь премиумом
    created_at = Column(TIMESTAMP, default=datetime.utcnow)  # Дата регистрации

    # Связи
    ratings = relationship("Rating", back_populates="user")  # Связь с оценками
    roles = relationship("UserRole", back_populates="user")  # Связь с ролями пользователя


# Таблица ролей (например, "Админ", "Обычный пользователь")
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)  # Уникальный ID роли
    name = Column(String(50), unique=True, nullable=False)  # Название роли (уникальное)

    # Связь: роль может быть у нескольких пользователей
    users = relationship("UserRole", back_populates="role")


# Промежуточная таблица для связи пользователей и ролей (многие ко многим)
class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)  # ID пользователя
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)  # ID роли

    user = relationship("User", back_populates="roles")  # Связь с пользователем
    role = relationship("Role", back_populates="users")  # Связь с ролью


# Таблица критериев оценки (например, "Вкус", "Цена", "Энергетический эффект")
class Criteria(Base):
    __tablename__ = "criteria"

    id = Column(Integer, primary_key=True, index=True)  # Уникальный ID критерия
    name = Column(String(100), unique=True, nullable=False)  # Название критерия

    # Связь: один критерий -> много оценок
    ratings = relationship("Rating", back_populates="criteria")


# Таблица оценок и отзывов
class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)  # Уникальный ID оценки
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # ID пользователя, который поставил оценку
    energy_id = Column(Integer, ForeignKey("energetics.id"), nullable=False)  # ID энергетика, которому поставили оценку
    criteria_id = Column(Integer, ForeignKey("criteria.id"), nullable=False)  # ID критерия оценки (например, "Вкус")
    rating = Column(Numeric(3, 1), nullable=False)  # Оценка от 0.0 до 10.0
    review = Column(Text, nullable=True)  # Отзыв (текстовое поле)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)  # Дата оставления отзыва

    # Определение связей
    user = relationship("User", back_populates="ratings")  # Связь с пользователем
    energy = relationship("Energy", back_populates="ratings")  # Связь с энергетиком
    criteria = relationship("Criteria", back_populates="ratings")  # Связь с критерием оценки

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Numeric, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional

# Создаем базовый класс для ORM-моделей
Base = declarative_base()

# ORM-модель для таблицы "brands" (бренды энергетиков)
class BrandOrm(Base):
    __tablename__ = "brands"

    # Уникальный идентификатор бренда (первичный ключ)
    id: Mapped[int] = mapped_column(primary_key=True)
    # Название бренда, строка длиной до 255 символов, уникальная и обязательная для заполнения
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

# ORM-модель для таблицы "energetics" (энергетики)
class EnergeticOrm(Base):
    __tablename__ = "energetics"

    # Уникальный идентификатор энергетика (первичный ключ)
    id: Mapped[int] = mapped_column(primary_key=True)
    # Название энергетика, строка длиной до 255 символов, не обязательное поле
    name: Mapped[Optional[str]] = mapped_column(String(255))
    # Внешний ключ на таблицу "brands", указывает на бренд энергетика
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"))
    # Внешний ключ на таблицу "categories", указывает на категорию энергетика (не обязательное поле)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"))
    # Описание энергетика, текстовое поле (не обязательное)
    description: Mapped[Optional[str]] = mapped_column(Text)
    # Состав энергетика, текстовое поле (не обязательное)
    ingredients: Mapped[Optional[str]] = mapped_column(Text)
    # URL изображения энергетика, строка длиной до 255 символов (не обязательное)
    image_url: Mapped[Optional[str]] = mapped_column(String(255))
    # Внешний ключ на таблицу "price_categories", указывает на ценовую категорию энергетика (не обязательное поле)
    price_category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("price_categories.id"))

# ORM-модель для таблицы "ratings" (рейтинги и отзывы пользователей)
class RatingOrm(Base):
    __tablename__ = "ratings"

    # Уникальный идентификатор рейтинга (первичный ключ)
    id: Mapped[int] = mapped_column(primary_key=True)
    # Внешний ключ на таблицу "users", указывает на пользователя, который оставил рейтинг
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # Внешний ключ на таблицу "energetics", указывает на энергетик, для которого оставлен рейтинг
    energy_id: Mapped[int] = mapped_column(ForeignKey("energetics.id"))
    # Оценка энергетика, числовое значение с точностью до 10 знаков после запятой (не обязательное поле)
    rating: Mapped[Optional[Numeric]] = mapped_column(Numeric(20, 10))
    # Текстовый отзыв пользователя (не обязательное поле)
    review: Mapped[Optional[str]] = mapped_column(Text)
    # Внешний ключ на таблицу "criteria", указывает на критерий оценки (не обязательное поле)
    criteria_id: Mapped[Optional[int]] = mapped_column(ForeignKey("criteria.id"))
    # Время создания отзыва, обязательное поле с типом TIMESTAMP
    created_at: Mapped[Optional[str]] = mapped_column(TIMESTAMP, nullable=False)
    # Флаг, указывающий, является ли запись исторической (по умолчанию False)
    is_history: Mapped[bool] = mapped_column(Boolean, default=False)
    # Внешний ключ на таблицу "ratings", указывает на оригинальный рейтинг (не обязательное поле)
    original_rating_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ratings.id"))

# ORM-модель для таблицы "users" (пользователи)
class UserOrm(Base):
    __tablename__ = "users"

    # Уникальный идентификатор пользователя (первичный ключ)
    id: Mapped[int] = mapped_column(primary_key=True)
    # Имя пользователя, строка длиной до 255 символов, уникальная и обязательная для заполнения
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

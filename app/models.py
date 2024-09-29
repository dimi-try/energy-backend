from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base
# from sqlalchemy.orm import Mapped, mapped_column
# from sqlalchemy import Integer, String, Text, Numeric, ForeignKey, TIMESTAMP, Boolean
# from sqlalchemy.ext.declarative import declarative_base
# from typing import Optional

class Brand(Base):
    __tablename__ = 'brand'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=64), unique=True, index=True)

    energies = relationship("Energy", back_populates="brand")


class Energy(Base):
    __tablename__ = 'energy'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=64), unique=True, index=True)  
    brand_id = Column(Integer, ForeignKey('brand.id'), nullable=False)
    description = Column(String)

    # Определение отношения между таблицами
    brand = relationship("Brand", back_populates="energies")

# # ORM-модель для таблицы "ratings" (рейтинги и отзывы пользователей)
# class RatingOrm(Base):
#     __tablename__ = "ratings"

#     # Уникальный идентификатор рейтинга (первичный ключ)
#     id: Mapped[int] = mapped_column(primary_key=True)
#     # Внешний ключ на таблицу "users", указывает на пользователя, который оставил рейтинг
#     user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
#     # Внешний ключ на таблицу "energetics", указывает на энергетик, для которого оставлен рейтинг
#     energy_id: Mapped[int] = mapped_column(ForeignKey("energetics.id"))
#     # Оценка энергетика, числовое значение с точностью до 10 знаков после запятой (не обязательное поле)
#     rating: Mapped[Optional[Numeric]] = mapped_column(Numeric(20, 10))
#     # Текстовый отзыв пользователя (не обязательное поле)
#     review: Mapped[Optional[str]] = mapped_column(Text)
#     # Внешний ключ на таблицу "criteria", указывает на критерий оценки (не обязательное поле)
#     criteria_id: Mapped[Optional[int]] = mapped_column(ForeignKey("criteria.id"))
#     # Время создания отзыва, обязательное поле с типом TIMESTAMP
#     created_at: Mapped[Optional[str]] = mapped_column(TIMESTAMP, nullable=False)
#     # Флаг, указывающий, является ли запись исторической (по умолчанию False)
#     is_history: Mapped[bool] = mapped_column(Boolean, default=False)
#     # Внешний ключ на таблицу "ratings", указывает на оригинальный рейтинг (не обязательное поле)
#     original_rating_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ratings.id"))

# # ORM-модель для таблицы "users" (пользователи)
# class UserOrm(Base):
#     __tablename__ = "users"

#     # Уникальный идентификатор пользователя (первичный ключ)
#     id: Mapped[int] = mapped_column(primary_key=True)
#     # Имя пользователя, строка длиной до 255 символов, уникальная и обязательная для заполнения
#     name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

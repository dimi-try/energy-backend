"""Модель предложки энергетика от пользователя.

Проходит через статусы:
    - pending   – ожидает модерации
    - approved  – одобрена, энергетик создан
    - rejected  – отклонена администратором

При одобрении может быть создан новый бренд, если пользователь указал `new_brand_name`.
Отзыв создается сразу при создании предложки с `suggestion_id`,
а `energy_id` заполняется при одобрении.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.db.models.base import Base

import enum


class SuggestionStatus(str, enum.Enum):
    """Статусы предложки."""
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Suggestion(Base):
    """Таблица предложок энергетиков."""
    __tablename__ = "suggestions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Основные данные энергетика
    name = Column(String(255), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    new_brand_name = Column(String(255), nullable=True)  # если бренда нет в списке
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    description = Column(Text, nullable=True)
    # URL изображения энергетика
    image_url = Column(String(512), nullable=True)
    
    # Статус и комментарий модератора
    status = Column(Enum(SuggestionStatus), default=SuggestionStatus.pending, nullable=False)
    admin_comment = Column(Text, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    user = relationship("User", back_populates="suggestions")
    brand = relationship("Brand", back_populates="suggestions")
    category = relationship("Category", back_populates="suggestions")
    # Один отзыв к предложке (связь через suggestion_id в Review)
    review = relationship("Review", back_populates="suggestion", uselist=False)

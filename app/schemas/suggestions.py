"""Pydantic схемы для модуля предложок."""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class BrandBrief(BaseModel):
    """Краткая информация о бренде."""
    id: int
    name: str

    class Config:
        orm_mode = True


class UserBrief(BaseModel):
    """Краткая информация о пользователе."""
    id: int
    username: str
    image_url: Optional[str] = None

    class Config:
        orm_mode = True


class CategoryBrief(BaseModel):
    """Краткая информация о категории."""
    id: int
    name: str

    class Config:
        orm_mode = True


class RatingItem(BaseModel):
    """Оценка по критерию."""
    criteria_id: int
    rating_value: float

    class Config:
        orm_mode = True


class ReviewBrief(BaseModel):
    """Краткая информация об отзыве к предложке."""
    id: int
    review_text: Optional[str] = None
    ratings: Optional[List[RatingItem]] = None

    class Config:
        orm_mode = True


class SuggestionBase(BaseModel):
    """Базовая схема предложки."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    brand_id: Optional[int] = None
    new_brand_name: Optional[str] = None
    category_id: int
    image_url: Optional[str] = None


class SuggestionCreate(SuggestionBase):
    """Схема создания предложки."""
    review_text: Optional[str] = None
    ratings: Optional[List[RatingItem]] = None


class SuggestionUpdate(BaseModel):
    """Схема обновления предложки."""
    name: Optional[str] = None
    description: Optional[str] = None
    brand_id: Optional[int] = None
    new_brand_name: Optional[str] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    review_text: Optional[str] = None
    ratings: Optional[List[RatingItem]] = None


class SuggestionOut(SuggestionBase):
    """Схема ответа для предложки пользователя."""
    id: int
    user_id: int
    status: str
    admin_comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    brand: Optional[BrandBrief] = None
    user: Optional[UserBrief] = None
    category: Optional[CategoryBrief] = None
    review: Optional[ReviewBrief] = None

    class Config:
        orm_mode = True


class SuggestionStatusOut(BaseModel):
    """Схема ответа для админ-панели."""
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    brand_id: Optional[int] = None
    new_brand_name: Optional[str] = None
    category_id: int
    image_url: Optional[str] = None
    status: str
    admin_comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    brand: Optional[BrandBrief] = None
    user: Optional[UserBrief] = None
    category: Optional[CategoryBrief] = None
    review: Optional[ReviewBrief] = None

    class Config:
        orm_mode = True

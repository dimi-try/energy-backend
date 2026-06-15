"""Сервисный слой для работы с предложками энергетиков."""

import os
import shutil
import uuid
from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from app.db import models
from app.schemas.suggestions import SuggestionCreate, SuggestionUpdate, RatingItem
from app.db.models.suggestion import SuggestionStatus
from app.db.models.brand import Brand
from app.db.models.energy import Energy
from app.db.models.review import Review
from app.db.models.rating import Rating
from app.core.config import UPLOAD_DIR_SUGGESTION, UPLOAD_DIR_REVIEW


def copy_suggestion_image_to_review(image_url: str | None) -> str | None:
    """Копирует фото предложки в папку отзывов и возвращает новый путь.
    
    Args:
        image_url: Путь к фото в папке предложок
        
    Returns:
        Путь к скопированному фото в папке отзывов или None
    """
    if not image_url:
        return None
    
    src_path = os.path.join(UPLOAD_DIR_SUGGESTION, os.path.basename(image_url))
    if not os.path.exists(src_path):
        return None
    
    # Генерируем уникальное имя файла
    ext = os.path.splitext(src_path)[1]
    new_filename = f"{uuid.uuid4()}{ext}"
    dst_path = os.path.join(UPLOAD_DIR_REVIEW, new_filename)
    
    shutil.copy2(src_path, dst_path)
    os.remove(src_path)  # Удаляем оригинал
    
    return f"{UPLOAD_DIR_REVIEW}/{new_filename}"


def _delete_suggestion_image(image_url: str | None):
    """Удаляет фото предложки если существует."""
    if image_url:
        filepath = os.path.join(UPLOAD_DIR_SUGGESTION, os.path.basename(image_url))
        if os.path.exists(filepath):
            os.remove(filepath)


def create_suggestion(db: Session, user_id: int, payload: SuggestionCreate):
    """Создает новую предложку с отзывом.
    
    Отзыв создается если есть хотя бы одна оценка (даже без текста отзыва).
    
    Args:
        db: Сессия базы данных
        user_id: ID пользователя
        payload: Данные предложки
        
    Returns:
        Созданная предложка
    """
    suggestion = models.suggestion.Suggestion(
        user_id=user_id,
        name=payload.name,
        description=payload.description,
        brand_id=payload.brand_id,
        new_brand_name=payload.new_brand_name,
        category_id=payload.category_id,
        image_url=payload.image_url,
    )
    db.add(suggestion)
    db.flush()
    
    # Создаем отзыв если есть оценки (даже без текста)
    if payload.ratings:
        review = Review(
            user_id=user_id,
            energy_id=None,  # Заполнится при одобрении
            suggestion_id=suggestion.id,
            review_text=payload.review_text or None,
            created_at=int(datetime.utcnow().timestamp()),
        )
        db.add(review)
        db.flush()
        
        # Создаем оценки к отзыву
        for rating_data in payload.ratings:
            rating = Rating(
                review_id=review.id,
                criteria_id=rating_data.criteria_id,
                rating_value=rating_data.rating_value,
            )
            db.add(rating)
    
    db.commit()
    db.refresh(suggestion)
    return suggestion


def get_user_suggestions(db: Session, user_id: int):
    """Получает все предложки пользователя.
    
    Args:
        db: Сессия базы данных
        user_id: ID пользователя
        
    Returns:
        Список предложок
    """
    return (
        db.query(models.suggestion.Suggestion)
        .options(joinedload(models.suggestion.Suggestion.brand))
        .options(joinedload(models.suggestion.Suggestion.category))
        .options(joinedload(models.suggestion.Suggestion.review).joinedload(models.review.Review.ratings))
        .filter_by(user_id=user_id)
        .all()
    )


def get_all_suggestions(db: Session):
    """Получает все предложки (для админ-панели).
    
    Args:
        db: Сессия базы данных
        
    Returns:
        Список всех предложок
    """
    return (
        db.query(models.suggestion.Suggestion)
        .options(joinedload(models.suggestion.Suggestion.brand))
        .options(joinedload(models.suggestion.Suggestion.user))
        .options(joinedload(models.suggestion.Suggestion.category))
        .options(joinedload(models.suggestion.Suggestion.review).joinedload(models.review.Review.ratings))
        .all()
    )


def update_suggestion(db: Session, user_id: int, suggestion_id: int, payload: SuggestionUpdate):
    """Обновляет предложку.
    
    Args:
        db: Сессия базы данных
        user_id: ID пользователя
        suggestion_id: ID предложки
        payload: Данные для обновления
        
    Returns:
        Обновленная предложка или None
    """
    suggestion = (
        db.query(models.suggestion.Suggestion)
        .options(joinedload(models.suggestion.Suggestion.review).joinedload(models.review.Review.ratings))
        .filter_by(id=suggestion_id, user_id=user_id)
        .first()
    )
    if not suggestion:
        return None
    if suggestion.status not in (SuggestionStatus.pending, SuggestionStatus.rejected):
        return None
    
    # Обновляем поля предложки
    if payload.name is not None:
        suggestion.name = payload.name
    if payload.description is not None:
        suggestion.description = payload.description
    if payload.brand_id is not None:
        suggestion.brand_id = payload.brand_id
    if payload.new_brand_name is not None:
        suggestion.new_brand_name = payload.new_brand_name
    if payload.category_id is not None:
        suggestion.category_id = payload.category_id
    if payload.image_url is not None:
        suggestion.image_url = payload.image_url
    
    # Обновляем отзыв если существует
    if suggestion.review:
        if payload.review_text is not None:
            suggestion.review.review_text = payload.review_text
        
        # Обновляем оценки если предоставлены
        if payload.ratings is not None:
            # Удаляем старые оценки
            for old_rating in suggestion.review.ratings:
                db.delete(old_rating)
            
            # Добавляем новые оценки
            for rating_data in payload.ratings:
                rating = Rating(
                    review_id=suggestion.review.id,
                    criteria_id=rating_data.criteria_id,
                    rating_value=rating_data.rating_value,
                )
                db.add(rating)
    
    # Сбрасываем статус если был отклонен
    if suggestion.status == SuggestionStatus.rejected:
        suggestion.status = SuggestionStatus.pending
        suggestion.admin_comment = None
    
    suggestion.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(suggestion)
    return suggestion


def approve_suggestion(db: Session, suggestion_id: int):
    """Одобряет предложку: создает бренд/энергетик, обновляет отзыв.
    
    Args:
        db: Сессия базы данных
        suggestion_id: ID предложки
        
    Returns:
        Созданный энергетик или None
    """
    suggestion = (
        db.query(models.suggestion.Suggestion)
        .options(joinedload(models.suggestion.Suggestion.user))
        .options(joinedload(models.suggestion.Suggestion.review))
        .filter_by(id=suggestion_id)
        .first()
    )
    if not suggestion or suggestion.status not in (SuggestionStatus.pending, SuggestionStatus.rejected):
        return None

    # Определяем или создаем бренд
    if suggestion.brand_id:
        brand = db.query(Brand).filter_by(id=suggestion.brand_id).first()
    else:
        # Если бренд не указан, создаем новый
        brand = Brand(name=suggestion.new_brand_name or "Unknown")
        db.add(brand)
        db.flush()

    # Создаем энергетик (без фото - фото идет в отзыв)
    energy = Energy(
        name=suggestion.name,
        brand_id=brand.id,
        category_id=suggestion.category_id,
        description=suggestion.description,
    )
    db.add(energy)
    db.flush()

    # Обновляем отзыв: устанавливаем energy_id и копируем фото
    if suggestion.review:
        suggestion.review.energy_id = energy.id
        review_image_url = copy_suggestion_image_to_review(suggestion.image_url)
        if review_image_url:
            suggestion.review.image_url = review_image_url

    # Обновляем статус предложки
    suggestion.status = SuggestionStatus.approved
    db.delete(suggestion)
    db.commit()
    return energy


def reject_suggestion(db: Session, suggestion_id: int, comment: str | None = None):
    """Отклоняет предложку.
    
    Args:
        db: Сессия базы данных
        suggestion_id: ID предложки
        comment: Комментарий администратора
        
    Returns:
        Отклоненная предложка или None
    """
    suggestion = db.query(models.suggestion.Suggestion).filter_by(id=suggestion_id).first()
    if not suggestion or suggestion.status not in (SuggestionStatus.pending, SuggestionStatus.rejected):
        return None
    
    suggestion.status = SuggestionStatus.rejected
    suggestion.admin_comment = comment
    db.commit()
    db.refresh(suggestion)
    return suggestion


def delete_suggestion(db: Session, user_id: int, suggestion_id: int):
    """Удаляет предложку и связанное фото.
    
    Args:
        db: Сессия базы данных
        user_id: ID пользователя
        suggestion_id: ID предложки
        
    Returns:
        True если удалено, иначе None
    """
    suggestion = (
        db.query(models.suggestion.Suggestion)
        .filter_by(id=suggestion_id, user_id=user_id)
        .first()
    )
    if not suggestion:
        return None
    if suggestion.status not in (SuggestionStatus.pending, SuggestionStatus.rejected):
        return None
    
    # Удаляем связанное фото
    _delete_suggestion_image(suggestion.image_url)
    
    db.delete(suggestion)
    db.commit()
    return True

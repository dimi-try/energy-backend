from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db

from app.schemas.ratings import Rating

from app.services.ratings import get_rating, get_ratings_by_review

# Создаём маршрутизатор для эндпоинтов оценок
router = APIRouter()

# Закомментированный эндпоинт для получения данных об оценке (пока что не нужен)
# # Данные о конкретной оценке
# @router.get("/ratings/{rating_id}", response_model=schemas.Rating)
# def read_rating(rating_id: int, db: Session = Depends(get_db)):
#     db_rating = crud.get_rating(db, rating_id=rating_id)
#     if not db_rating:
#         raise HTTPException(status_code=404, detail="Rating not found")
#     return db_rating


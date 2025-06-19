# Импортируем APIRouter из FastAPI для создания маршрутов
from fastapi import APIRouter, Depends, HTTPException
# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем List из typing для аннотации списков
from typing import List
# Импортируем функции CRUD для оценок
from app.services.rating import get_rating, get_ratings_by_review
# Импортируем схемы для оценок
from app.schemas.rating import Rating
# Импортируем зависимость для получения сессии базы данных
from app.db.database import get_db

# Создаём маршрутизатор для эндпоинтов оценок
router = APIRouter()

# Закомментированный эндпоинт для получения данных об оценке (сохранён как есть)
# # Данные о конкретной оценке
# @router.get("/ratings/{rating_id}", response_model=schemas.Rating)
# def read_rating(rating_id: int, db: Session = Depends(get_db)):
#     db_rating = crud.get_rating(db, rating_id=rating_id)
#     if not db_rating:
#         raise HTTPException(status_code=404, detail="Rating not found")
#     return db_rating


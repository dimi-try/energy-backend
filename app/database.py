import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .config import DATABASE_URL

if not DATABASE_URL:
    raise ValueError("DATABASE_URL не задан! Проверь .env файл или переменные окружения.")

# Создаём движок для PostgreSQL
engine = create_engine(DATABASE_URL)

# Создаём фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# ===================== DEPENDENCY =====================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
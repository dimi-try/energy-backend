# Импортируем declarative_base из SQLAlchemy для создания базового класса
from sqlalchemy.ext.declarative import declarative_base

# Создаём базовый класс для всех моделей
Base = declarative_base()
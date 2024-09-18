from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем URL базы данных из переменной окружения
DATABASE_URL = os.getenv('DATABASE_URL')

# Создаем асинхронный движок для работы с базой данных с помощью SQLAlchemy
# create_async_engine создаёт движок для асинхронного взаимодействия с базой данных
engine = create_async_engine(DATABASE_URL)

# Создаем фабрику асинхронных сессий для взаимодействия с базой данных
# async_sessionmaker - это фабрика для создания сессий (подключений к базе)
# expire_on_commit=False - предотвращает автоматическое "устаревание" данных после коммита, что полезно для длительных операций
async_session = async_sessionmaker(engine, expire_on_commit=False)


# Базовый класс для всех моделей базы данных (ORM моделей)
# Все ORM-модели будут наследоваться от этого класса
class Base(DeclarativeBase):
    pass


# Функция для создания всех таблиц в базе данных, если они не существуют
# Используется метод run_sync для выполнения синхронной операции с метаданными модели
# Base.metadata.create_all создает таблицы для всех моделей, унаследованных от Base
async def create_db():
    async with engine.begin() as conn:  # Открываем соединение с базой данных
        await conn.run_sync(Base.metadata.create_all)  # Выполняем команду создания таблиц


# Функция для закрытия соединения с базой данных
# Используется для освобождения ресурсов, когда приложение завершает работу
async def close_db():
    await engine.dispose()  # Закрываем движок и освобождаем ресурсы

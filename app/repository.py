from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from app.models import EnergeticOrm, BrandOrm, RatingOrm, UserOrm
from app.schemas import EnergeticModel, RatingModel, BrandModel, UserModel

# Репозиторий для работы с энергетиками
class EnergeticRepository:
    # Метод для получения всех энергетиков с информацией о средней оценке
    @classmethod
    async def get_all(cls) -> list[EnergeticModel]:
        async with async_session() as session:
            # Подзапрос для вычисления среднего рейтинга для каждого энергетика
            subquery = (
                select(
                    RatingOrm.energy_id,
                    func.avg(RatingOrm.rating).label("avg_rating")
                )
                .group_by(RatingOrm.energy_id)  # Группируем по энергетикам
                .subquery()
            )
            
            # Основной запрос для получения энергетиков и их среднего рейтинга
            query = (
                select(
                    EnergeticOrm.id,
                    EnergeticOrm.name,
                    BrandOrm.id.label("brand_id"),
                    BrandOrm.name.label("brand_name"),
                    func.coalesce(subquery.c.avg_rating, 0).label("rating")  # Используем coalesce для обработки случаев с отсутствием рейтинга
                )
                .join(BrandOrm, EnergeticOrm.brand_id == BrandOrm.id)  # Соединяем таблицы энергетиков и брендов
                .outerjoin(subquery, EnergeticOrm.id == subquery.c.energy_id)  # Внешнее соединение с подзапросом среднего рейтинга
            )
            
            result = await session.execute(query)
            energetics = result.fetchall()  # Извлекаем все строки результата
            
            # Преобразуем результат запроса в список объектов EnergeticModel
            return [
                EnergeticModel(
                    id=row[0],
                    name=row[1],
                    brand={"id": row[2], "name": row[3]},
                    rating=row[4],
                )
                for row in energetics
            ]
    
    # Метод для получения энергетиков по id бренда с информацией о средней оценке
    @classmethod
    async def get_by_brand_id(cls, brand_id: int) -> list[EnergeticModel]:
        async with async_session() as session:
            # Подзапрос для вычисления среднего рейтинга для энергетиков
            subquery = (
                select(
                    RatingOrm.energy_id,
                    func.avg(RatingOrm.rating).label("avg_rating")
                )
                .group_by(RatingOrm.energy_id)  # Группируем по id энергетиков
                .subquery()
            )
            
            # Основной запрос для получения энергетиков указанного бренда и их среднего рейтинга
            query = (
                select(
                    EnergeticOrm.id,
                    EnergeticOrm.name,
                    func.coalesce(subquery.c.avg_rating, 0).label("rating")
                )
                .join(subquery, EnergeticOrm.id == subquery.c.energy_id, isouter=True)  # Внешнее соединение с подзапросом рейтинга
                .filter(EnergeticOrm.brand_id == brand_id)  # Фильтрация по id бренда
            )
            
            result = await session.execute(query)
            energetics = result.fetchall()
            
            # Преобразуем результат запроса в список объектов EnergeticModel
            return [
                EnergeticModel(
                    id=row[0],
                    name=row[1],
                    brand={"id": brand_id, "name": "Unknown"},  # Можно добавить логику для получения названия бренда
                    rating=row[2],
                )
                for row in energetics
            ]

# Репозиторий для работы с отзывами
class RatingRepository:
    # Метод для добавления нового отзыва
    @classmethod
    async def add_rating(cls, user_id: int, rating_data: RatingModel):
        async with async_session() as session:
            # Создаем новый объект RatingOrm
            rating = RatingOrm(
                user_id=user_id,
                energy_id=rating_data.energy_id,
                rating=rating_data.rating,
                review=rating_data.review,
                criteria_id=rating_data.criteria_id,
                created_at=rating_data.created_at,
                is_history=rating_data.is_history,
                original_rating_id=rating_data.original_rating_id
            )
            session.add(rating)  # Добавляем отзыв в сессию
            await session.commit()  # Сохраняем изменения в базе данных

    # Метод для обновления отзыва
    @classmethod
    async def update_rating(cls, rating_id: int, user_id: int, rating_data: RatingModel):
        async with async_session() as session:
            # Запрашиваем отзыв по его id и id пользователя
            query = select(RatingOrm).filter_by(id=rating_id, user_id=user_id)
            result = await session.execute(query)
            rating = result.scalar_one_or_none()  # Получаем один результат или None, если отзыв не найден
            if rating:
                # Обновляем поля отзыва
                rating.rating = rating_data.rating
                rating.review = rating_data.review
                rating.criteria_id = rating_data.criteria_id
                rating.created_at = rating_data.created_at
                rating.is_history = rating_data.is_history
                rating.original_rating_id = rating_data.original_rating_id
                await session.commit()  # Сохраняем изменения в базе данных
            else:
                raise HTTPException(status_code=404, detail="Rating not found")  # Ошибка, если отзыв не найден

    # Метод для удаления отзыва
    @classmethod
    async def delete_rating(cls, rating_id: int, user_id: int):
        async with async_session() as session:
            # Запрашиваем отзыв по его id и id пользователя
            query = select(RatingOrm).filter_by(id=rating_id, user_id=user_id)
            result = await session.execute(query)
            rating = result.scalar_one_or_none()  # Получаем отзыв или None, если он не найден
            if rating:
                await session.delete(rating)  # Удаляем отзыв
                await session.commit()  # Сохраняем изменения в базе данных
            else:
                raise HTTPException(status_code=404, detail="Rating not found")  # Ошибка, если отзыв не найден

    # Метод для получения всех отзывов по id энергетика
    @classmethod
    async def get_ratings_by_energy(cls, energy_id: int) -> list[RatingModel]:
        async with async_session() as session:
            query = select(RatingOrm).filter_by(energy_id=energy_id)
            result = await session.execute(query)
            ratings = result.scalars().all()  # Получаем список отзывов
            return [
                RatingModel(
                    id=rating.id,
                    user_id=rating.user_id,
                    energy_id=rating.energy_id,
                    rating=rating.rating,
                    review=rating.review,
                    criteria_id=rating.criteria_id,
                    created_at=rating.created_at,
                    is_history=rating.is_history,
                    original_rating_id=rating.original_rating_id
                )
                for rating in ratings
            ]

    # Метод для получения всех отзывов пользователя по его id
    @classmethod
    async def get_ratings_by_user(cls, user_id: int) -> list[RatingModel]:
        async with async_session() as session:
            query = select(RatingOrm).filter_by(user_id=user_id)
            result = await session.execute(query)
            ratings = result.scalars().all()  # Получаем список отзывов
            return [
                RatingModel(
                    id=rating.id,
                    user_id=rating.user_id,
                    energy_id=rating.energy_id,
                    rating=rating.rating,
                    review=rating.review,
                    criteria_id=rating.criteria_id,
                    created_at=rating.created_at,
                    is_history=rating.is_history,
                    original_rating_id=rating.original_rating_id
                )
                for rating in ratings
            ]

# Репозиторий для работы с брендами
class BrandRepository:
    # Метод для получения всех брендов с их средним рейтингом
    @classmethod
    async def get_all(cls) -> list[BrandModel]:
        async with async_session() as session:
            # Подзапрос для вычисления среднего рейтинга для брендов
            subquery = (
                select(
                    EnergeticOrm.brand_id,
                    func.avg(RatingOrm.rating).label("avg_rating")
                )
                .join(RatingOrm, RatingOrm.energy_id == EnergeticOrm.id)
                .group_by(EnergeticOrm.brand_id)  # Группировка по id бренда
                .subquery()
            )

            # Основной запрос для получения данных о брендах и их среднем рейтинге
            query = (
                select(
                    BrandOrm.id,
                    BrandOrm.name,
                    func.coalesce(subquery.c.avg_rating, 0).label("average_rating")
                )
                .outerjoin(subquery, BrandOrm.id == subquery.c.brand_id)  # Внешнее соединение с подзапросом
            )

            result = await session.execute(query)
            brands = result.fetchall()  # Получаем все бренды
            
            # Преобразуем результат запроса в список объектов BrandModel
            return [
                BrandModel(
                    id=row[0],
                    name=row[1],
                    average_rating=row[2],
                )
                for row in brands
            ]

    # Метод для получения среднего рейтинга для конкретного бренда
    @classmethod
    async def get_average_rating_for_brand(cls, brand_id: int) -> float:
        async with async_session() as session:
            # Подзапрос для вычисления среднего рейтинга для бренда
            subquery = (
                select(
                    func.avg(RatingOrm.rating).label("avg_rating")
                )
                .join(EnergeticOrm, RatingOrm.energy_id == EnergeticOrm.id)
                .filter(EnergeticOrm.brand_id == brand_id)  # Фильтрация по id бренда
                .subquery()
            )
            
            # Выполнение запроса для получения среднего рейтинга
            query = select(func.coalesce(subquery.c.avg_rating, 0))
            result = await session.execute(query)
            return result.scalar_one_or_none() or 0  # Возвращаем результат или 0, если нет рейтинга

# Репозиторий для работы с пользователями
class UserRepository:
    # Метод для получения данных о пользователе по его id
    @classmethod
    async def get_user_by_id(cls, user_id: int) -> UserModel:
        async with async_session() as session:
            query = select(UserOrm).filter_by(id=user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()  # Получаем одного пользователя или None, если не найден
            if user:
                # Преобразуем результат запроса в объект UserModel
                return UserModel(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    created_at=user.created_at
                )
            else:
                raise HTTPException(status_code=404, detail="User not found")  # Ошибка, если пользователь не найден

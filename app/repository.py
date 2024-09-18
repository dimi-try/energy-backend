from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from app.models import EnergeticOrm, BrandOrm, RatingOrm, UserOrm
from app.schemas import EnergeticModel, RatingModel, BrandModel, UserModel

class EnergeticRepository:
    @classmethod
    async def get_all(cls) -> list[EnergeticModel]:
        async with async_session() as session:
            # Определяем подзапрос для получения среднего рейтинга
            subquery = (
                select(
                    RatingOrm.energy_id,
                    func.avg(RatingOrm.rating).label("avg_rating")
                )
                .group_by(RatingOrm.energy_id)
                .subquery()
            )
            
            # Основной запрос для получения данных энергетиков с их рейтингом
            query = (
                select(
                    EnergeticOrm.id,
                    EnergeticOrm.name,
                    BrandOrm.id.label("brand_id"),
                    BrandOrm.name.label("brand_name"),
                    func.coalesce(subquery.c.avg_rating, 0).label("rating")
                )
                .join(BrandOrm, EnergeticOrm.brand_id == BrandOrm.id)
                .outerjoin(subquery, EnergeticOrm.id == subquery.c.energy_id)
            )
            
            result = await session.execute(query)
            energetics = result.fetchall()
            
            return [
                EnergeticModel(
                    id=row[0],
                    name=row[1],
                    brand={"id": row[2], "name": row[3]},
                    rating=row[4],
                )
                for row in energetics
            ]
     
    @classmethod
    async def get_by_brand_id(cls, brand_id: int) -> list[EnergeticModel]:
        async with async_session() as session:
            # Определяем подзапрос для получения среднего рейтинга
            subquery = (
                select(
                    RatingOrm.energy_id,
                    func.avg(RatingOrm.rating).label("avg_rating")
                )
                .group_by(RatingOrm.energy_id)
                .subquery()
            )
            
            # Запрос для получения всех энергетиков для указанного бренда с рейтингом
            query = (
                select(
                    EnergeticOrm.id,
                    EnergeticOrm.name,
                    func.coalesce(subquery.c.avg_rating, 0).label("rating")
                )
                .join(subquery, EnergeticOrm.id == subquery.c.energy_id, isouter=True)
                .filter(EnergeticOrm.brand_id == brand_id)
            )
            
            result = await session.execute(query)
            energetics = result.fetchall()
            
            return [
                EnergeticModel(
                    id=row[0],
                    name=row[1],
                    brand={"id": brand_id, "name": "Unknown"},  # Brand name could be set based on brand_id if needed
                    rating=row[2],
                )
                for row in energetics
            ]

class RatingRepository:
    @classmethod
    async def add_rating(cls, user_id: int, rating_data: RatingModel):
        async with async_session() as session:
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
            session.add(rating)
            await session.commit()

    @classmethod
    async def update_rating(cls, rating_id: int, user_id: int, rating_data: RatingModel):
        async with async_session() as session:
            query = select(RatingOrm).filter_by(id=rating_id, user_id=user_id)
            result = await session.execute(query)
            rating = result.scalar_one_or_none()
            if rating:
                rating.rating = rating_data.rating
                rating.review = rating_data.review
                rating.criteria_id = rating_data.criteria_id
                rating.created_at = rating_data.created_at
                rating.is_history = rating_data.is_history
                rating.original_rating_id = rating_data.original_rating_id
                await session.commit()
            else:
                raise HTTPException(status_code=404, detail="Rating not found")

    @classmethod
    async def delete_rating(cls, rating_id: int, user_id: int):
        async with async_session() as session:
            query = select(RatingOrm).filter_by(id=rating_id, user_id=user_id)
            result = await session.execute(query)
            rating = result.scalar_one_or_none()
            if rating:
                await session.delete(rating)
                await session.commit()
            else:
                raise HTTPException(status_code=404, detail="Rating not found")

    @classmethod
    async def get_ratings_by_energy(cls, energy_id: int) -> list[RatingModel]:
        async with async_session() as session:
            query = select(RatingOrm).filter_by(energy_id=energy_id)
            result = await session.execute(query)
            ratings = result.scalars().all()
            return [RatingModel(
                id=rating.id,
                user_id=rating.user_id,
                energy_id=rating.energy_id,
                rating=rating.rating,
                review=rating.review,
                criteria_id=rating.criteria_id,
                created_at=rating.created_at,
                is_history=rating.is_history,
                original_rating_id=rating.original_rating_id
            ) for rating in ratings]

    @classmethod
    async def get_ratings_by_user(cls, user_id: int) -> list[RatingModel]:
        async with async_session() as session:
            query = select(RatingOrm).filter_by(user_id=user_id)
            result = await session.execute(query)
            ratings = result.scalars().all()
            return [RatingModel(
                id=rating.id,
                user_id=rating.user_id,
                energy_id=rating.energy_id,
                rating=rating.rating,
                review=rating.review,
                criteria_id=rating.criteria_id,
                created_at=rating.created_at,
                is_history=rating.is_history,
                original_rating_id=rating.original_rating_id
            ) for rating in ratings]

class BrandRepository:
    @classmethod
    async def get_all(cls) -> list[BrandModel]:
        async with async_session() as session:
            # Подзапрос для получения среднего рейтинга для каждого бренда
            subquery = (
                select(
                    EnergeticOrm.brand_id,
                    func.avg(RatingOrm.rating).label("avg_rating")
                )
                .join(RatingOrm, RatingOrm.energy_id == EnergeticOrm.id)
                .group_by(EnergeticOrm.brand_id)
                .subquery()
            )

            # Основной запрос для получения данных о брендах и их среднем рейтинге
            query = (
                select(
                    BrandOrm.id,
                    BrandOrm.name,
                    func.coalesce(subquery.c.avg_rating, 0).label("average_rating")
                )
                .outerjoin(subquery, BrandOrm.id == subquery.c.brand_id)
            )

            result = await session.execute(query)
            brands = result.fetchall()
            
            return [
                BrandModel(
                    id=row[0],
                    name=row[1],
                    average_rating=row[2],
                )
                for row in brands
            ]

    @classmethod
    async def get_average_rating_for_brand(cls, brand_id: int) -> float:
        async with async_session() as session:
            # Подзапрос для получения среднего рейтинга для указанного бренда
            subquery = (
                select(
                    func.avg(RatingOrm.rating).label("avg_rating")
                )
                .join(EnergeticOrm, RatingOrm.energy_id == EnergeticOrm.id)
                .filter(EnergeticOrm.brand_id == brand_id)
                .subquery()
            )
            
            query = select(func.coalesce(subquery.c.avg_rating, 0))
            result = await session.execute(query)
            return result.scalar_one_or_none() or 0

class UserRepository:
    @classmethod
    async def get_user_by_id(cls, user_id: int) -> UserModel:
        async with async_session() as session:
            query = select(UserOrm).filter_by(id=user_id)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            if user:
                return UserModel(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    created_at=user.created_at
                )
            else:
                raise HTTPException(status_code=404, detail="User not found")

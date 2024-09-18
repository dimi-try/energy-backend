from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from app.models import EnergeticOrm, BrandOrm, RatingOrm
from app.schemas import EnergeticModel

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

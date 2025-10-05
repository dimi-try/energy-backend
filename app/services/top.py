from sqlalchemy.orm import Session
from sqlalchemy import func, desc, distinct, or_
from sqlalchemy.sql.expression import func as sql_func

from app.db.models import Energy, Review, Rating, Brand
from app.schemas.top import EnergyTop, BrandTop

# =============== READ ENERGY CHART ===============
def get_top_energies(
    db: Session,
    limit: int = 10,
    offset: int = 0,
    search_query: str = None,
    min_rating: float = None,
    max_rating: float = None
):
    # Подзапрос для среднего рейтинга
    avg_rating_subquery = (
        db.query(
            Review.energy_id,
            func.round(func.avg(Rating.rating_value), 4).label('avg_rating')
        )
        .join(Rating)
        .group_by(Review.energy_id)
        .subquery()
    )

    # Подзапрос для количества отзывов
    review_count_subquery = (
        db.query(
            Review.energy_id,
            func.count(Review.id).label('review_count')
        )
        .group_by(Review.energy_id)
        .subquery()
    )

    # Подзапрос для вычисления абсолютного ранга (без фильтров)
    absolute_rank_subquery = (
        db.query(
            Energy.id.label('energy_id'),
            sql_func.row_number().over(
                order_by=[
                    desc(func.coalesce(avg_rating_subquery.c.avg_rating, 0)),
                    desc(func.coalesce(review_count_subquery.c.review_count, 0)),
                    Brand.name,
                    Energy.name
                ]
            ).label('absolute_rank')
        )
        .join(Brand)
        .outerjoin(avg_rating_subquery, Energy.id == avg_rating_subquery.c.energy_id)
        .outerjoin(review_count_subquery, Energy.id == review_count_subquery.c.energy_id)
        .group_by(Energy.id, Brand.name, avg_rating_subquery.c.avg_rating, review_count_subquery.c.review_count)
        .subquery()
    )

    # Основной запрос
    query = (
        db.query(
            Energy,
            func.coalesce(avg_rating_subquery.c.avg_rating, 0).label('average_rating'),
            func.coalesce(review_count_subquery.c.review_count, 0).label('review_count'),
            absolute_rank_subquery.c.absolute_rank
        )
        .outerjoin(avg_rating_subquery, Energy.id == avg_rating_subquery.c.energy_id)
        .outerjoin(review_count_subquery, Energy.id == review_count_subquery.c.energy_id)
        .outerjoin(absolute_rank_subquery, Energy.id == absolute_rank_subquery.c.energy_id)
        .join(Brand)
    )

    # Применяем фильтры
    if search_query:
        search_terms = search_query.lower().split()
        for term in search_terms:
            search_pattern = f"%{term}%"
            query = query.filter(
                or_(
                    func.lower(Energy.name).like(search_pattern),
                    func.lower(Brand.name).like(search_pattern)
                )
            )

    if min_rating is not None:
        query = query.filter(avg_rating_subquery.c.avg_rating >= min_rating)
    if max_rating is not None:
        query = query.filter(avg_rating_subquery.c.avg_rating <= max_rating)

    # Сортировка и пагинация
    energies = (
        query
        .order_by(
            desc(func.coalesce(
                avg_rating_subquery.c.avg_rating, 0
            )),  # Сортировка по числовому значению среднего рейтинга
            desc(func.coalesce(
                review_count_subquery.c.review_count, 0
            )),  # Сортировка по числовому значению количества отзывов
            Brand.name,
            Energy.name
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [{
        "id": energy.id,
        "name": energy.name,
        "average_rating": float(avg_rating),
        "brand": energy.brand,
        "category": energy.category,
        "image_url": energy.image_url,
        "review_count": review_count,
        "absolute_rank": absolute_rank
    } for energy, avg_rating, review_count, absolute_rank in energies]

# =============== READ BRAND CHART ===============
def get_top_brands(
    db: Session,
    limit: int = 10,
    offset: int = 0,
    search_query: str = None,
    min_rating: float = None,
    max_rating: float = None
):
    # Подзапрос для среднего рейтинга энергетиков бренда
    energy_avg_subquery = (
        db.query(
            Energy.brand_id,
            func.avg(Rating.rating_value).label("energy_avg_rating"),
        )
        .outerjoin(Review, Energy.id == Review.energy_id)
        .outerjoin(Rating, Review.id == Rating.review_id)
        .group_by(Energy.id)
        .subquery()
    )

    # Подзапрос для абсолютного ранга (без фильтров)
    absolute_rank_subquery = (
        db.query(
            Brand.id.label('brand_id'),
            sql_func.row_number().over(
                order_by=[
                    desc(func.coalesce(
                        func.avg(energy_avg_subquery.c.energy_avg_rating), 0
                    )),  # Используем тот же подзапрос для среднего рейтинга
                    desc(func.count(distinct(Energy.id))),  # Сортировка по количеству энергетиков
                    desc(func.count(distinct(Review.id))),  # Сортировка по количеству отзывов
                    Brand.name  # Сортировка по названию бренда
                ]
            ).label('absolute_rank')
        )
        .outerjoin(Energy, Brand.id == Energy.brand_id)
        .outerjoin(energy_avg_subquery, Brand.id == energy_avg_subquery.c.brand_id)
        .outerjoin(Review, Energy.id == Review.energy_id)
        .outerjoin(Rating, Review.id == Rating.review_id)
        .group_by(Brand.id)
        .subquery()
    )

    # Основной запрос
    query = (
        db.query(
            Brand.id,
            Brand.name,
            func.coalesce(
                func.round(func.avg(energy_avg_subquery.c.energy_avg_rating), 4), 0
            ).label("average_rating"),
            func.count(distinct(Energy.id)).label("energy_count"),
            func.count(distinct(Review.id)).label("review_count"),
            func.count(distinct(Rating.id)).label("rating_count"),
            absolute_rank_subquery.c.absolute_rank
        )
        .outerjoin(Energy, Brand.id == Energy.brand_id)
        .outerjoin(energy_avg_subquery, Brand.id == energy_avg_subquery.c.brand_id)
        .outerjoin(Review, Energy.id == Review.energy_id)
        .outerjoin(Rating, Review.id == Rating.review_id)
        .outerjoin(absolute_rank_subquery, Brand.id == absolute_rank_subquery.c.brand_id)
    )

    # Применяем фильтры
    if search_query:
        search_terms = search_query.lower().split()
        for term in search_terms:
            search_pattern = f"%{term}%"
            query = query.filter(func.lower(Brand.name).like(search_pattern))

    # Фильтр по среднему рейтингу бренда (average_rating)
    if min_rating is not None:
        query = query.having(
            func.coalesce(
                func.round(func.avg(energy_avg_subquery.c.energy_avg_rating), 4), 0
            ) >= min_rating
        )
    if max_rating is not None:
        query = query.having(
            func.coalesce(
                func.round(func.avg(energy_avg_subquery.c.energy_avg_rating), 4), 0
            ) <= max_rating
        )

    # Группировка, сортировка и пагинация
    results = (
        query
        .group_by(Brand.id, absolute_rank_subquery.c.absolute_rank)
        .order_by(
            desc(func.coalesce(
                func.avg(energy_avg_subquery.c.energy_avg_rating), 0
            )),  # 1. По среднему рейтингу (по убыванию)
            desc(func.count(distinct(Energy.id))),  # 2. По количеству энергетиков (по убыванию)
            desc(func.count(distinct(Review.id))),  # 3. По количеству отзывов (по убыванию)
            Brand.name  # 4. По названию бренда (по возрастанию)
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": brand_id,
            "name": name,
            "average_rating": float(average_rating),
            "energy_count": energy_count,
            "review_count": review_count,
            "rating_count": rating_count,
            "absolute_rank": absolute_rank
        }
        for brand_id, name, average_rating, energy_count, review_count, rating_count, absolute_rank in results
    ]

# =============== READ TOTAL ENERGY COUNT ===============
def get_total_energies(db: Session, search_query: str = None, min_rating: float = None, max_rating: float = None):
    avg_rating_subquery = (
        db.query(
            Review.energy_id,
            func.round(func.avg(Rating.rating_value), 4).label('avg_rating')
        )
        .join(Rating)
        .group_by(Review.energy_id)
        .subquery()
    )

    query = (
        db.query(Energy)
        .join(Brand)
        .outerjoin(avg_rating_subquery, Energy.id == avg_rating_subquery.c.energy_id)
    )

    if search_query:
        search_terms = search_query.lower().split()
        for term in search_terms:
            search_pattern = f"%{term}%"
            query = query.filter(
                or_(
                    func.lower(Energy.name).like(search_pattern),
                    func.lower(Brand.name).like(search_pattern)
                )
            )

    if min_rating is not None:
        query = query.filter(avg_rating_subquery.c.avg_rating >= min_rating)
    if max_rating is not None:
        query = query.filter(avg_rating_subquery.c.avg_rating <= max_rating)

    return query.count()

# =============== READ TOTAL BRAND COUNT ===============
def get_total_brands(db: Session, search_query: str = None, min_rating: float = None, max_rating: float = None):
    energy_avg_subquery = (
        db.query(
            Energy.brand_id,
            func.avg(Rating.rating_value).label("energy_avg_rating"),
        )
        .outerjoin(Review, Energy.id == Review.energy_id)
        .outerjoin(Rating, Review.id == Rating.review_id)
        .group_by(Energy.id)
        .subquery()
    )

    query = (
        db.query(Brand)
        .outerjoin(Energy, Brand.id == Energy.brand_id)
        .outerjoin(energy_avg_subquery, Brand.id == energy_avg_subquery.c.brand_id)
    )

    if search_query:
        search_terms = search_query.lower().split()
        for term in search_terms:
            search_pattern = f"%{term}%"
            query = query.filter(func.lower(Brand.name).like(search_pattern))

    # Фильтр по среднему рейтингу бренда для подсчета
    if min_rating is not None:
        query = query.having(
            func.coalesce(
                func.round(func.avg(energy_avg_subquery.c.energy_avg_rating), 4), 0
            ) >= min_rating
        )
    if max_rating is not None:
        query = query.having(
            func.coalesce(
                func.round(func.avg(energy_avg_subquery.c.energy_avg_rating), 4), 0
            ) <= max_rating
        )

    return query.group_by(Brand.id).count()
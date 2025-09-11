from sqlalchemy.orm import Session
from sqlalchemy import func, desc, distinct

from app.db.models import Energy, Review, Rating, Brand

from app.schemas.top import EnergyTop, BrandTop

# =============== READ ENERGY CHART ===============
def get_top_energies(db: Session, limit: int = 10, offset: int = 0):
    # Создаём подзапрос для среднего рейтинга
    avg_rating_subquery = (
        # Начинаем запрос с таблицы Review
        db.query(
            # Выбираем energy_id
            Review.energy_id,
            # Вычисляем средний рейтинг
            func.round(func.avg(Rating.rating_value), 4).label('avg_rating')
        )
        # Присоединяем таблицу Rating
        .join(Rating)
        # Группируем по energy_id
        .group_by(Review.energy_id)
        # Преобразуем в подзапрос
        .subquery()
    )

    # Создаём подзапрос для количества отзывов
    review_count_subquery = (
        # Начинаем запрос с таблицы Review
        db.query(
            # Выбираем energy_id
            Review.energy_id,
            # Считаем отзывы
            func.count(Review.id).label('review_count')
        )
        # Группируем по energy_id
        .group_by(Review.energy_id)
        # Преобразуем в подзапрос
        .subquery()
    )

    # Выполняем запрос для топа энергетиков
    energies = (
        # Начинаем запрос с таблицы Energy
        db.query(
            # Выбираем объект Energy
            Energy,
            # Устанавливаем средний рейтинг
            func.coalesce(avg_rating_subquery.c.avg_rating, 0).label('average_rating'),
            # Устанавливаем количество отзывов
            func.coalesce(review_count_subquery.c.review_count, 0).label('review_count')
        )
        # Левое соединение с подзапросом рейтинга
        .outerjoin(avg_rating_subquery, Energy.id == avg_rating_subquery.c.energy_id)
        # Левое соединение с подзапросом отзывов
        .outerjoin(review_count_subquery, Energy.id == review_count_subquery.c.energy_id)
        # Присоединяем таблицу Brand
        .join(Brand)
        # Сортируем результаты
        .order_by(
            # По рейтингу
            desc('average_rating'),
            # По количеству отзывов
            desc('review_count'),
            # По названию бренда
            Brand.name,
            # По названию энергетика
            Energy.name
        )
        # Ограничиваем записи
        .offset(offset)  # Добавляем смещение
        .limit(limit)    # Ограничиваем количество записей
        # Получаем результаты
        .all()
    )

    # Преобразуем результаты
    return [{
        # Устанавливаем id
        "id": energy.id,
        # Устанавливаем название
        "name": energy.name,
        # Устанавливаем рейтинг
        "average_rating": float(avg_rating),
        # Устанавливаем бренд
        "brand": energy.brand,
        # Устанавливаем категорию
        "category": energy.category,
        # Устанавливаем изображение
        "image_url": energy.image_url,
        # Устанавливаем количество отзывов
        "review_count": review_count
    } for energy, avg_rating, review_count in energies]

# =============== READ BRAND CHART ===============
def get_top_brands(db: Session, limit: int = 10, offset: int = 0):
    """
    Получает топ брендов с:
    - Средним рейтингом (правильный расчет)
    - Количеством энергетиков
    - Количеством отзывов
    - Количеством оценок
    - Сортировкой по рейтингу
    Используется в эндпоинте GET /top/brands/, доступном всем пользователям.
    """
    # Создаём подзапрос для рейтингов
    energy_avg_subquery = (
        # Начинаем запрос с таблицы Energy
        db.query(
            # Выбираем brand_id
            Energy.brand_id,
            # Вычисляем средний рейтинг
            func.avg(Rating.rating_value).label("energy_avg_rating"),
        )
        # Левое соединение с таблицей Review
        .outerjoin(Review, Energy.id == Review.energy_id)
        # Левое соединение с таблицей Rating
        .outerjoin(Rating, Review.id == Rating.review_id)
        # Группируем по id энергетика
        .group_by(Energy.id)
        # Преобразуем в подзапрос
        .subquery()
    )

    # Выполняем запрос для топа брендов
    results = (
        # Начинаем запрос с таблицы Brand
        db.query(
            # Выбираем id бренда
            Brand.id,
            # Выбираем название бренда
            Brand.name,
            # Вычисляем средний рейтинг
            func.coalesce(func.round(func.avg(energy_avg_subquery.c.energy_avg_rating), 4), 0).label("average_rating"),
            # Считаем количество энергетиков
            func.count(distinct(Energy.id)).label("energy_count"),
            # Считаем количество отзывов
            func.count(distinct(Review.id)).label("review_count"),
            # Считаем количество оценок
            func.count(distinct(Rating.id)).label("rating_count"),
        )
        # Левое соединение с таблицей Energy
        .outerjoin(Energy, Brand.id == Energy.brand_id)
        # Левое соединение с подзапросом
        .outerjoin(energy_avg_subquery, Brand.id == energy_avg_subquery.c.brand_id)
        # Левое соединение с таблицей Review
        .outerjoin(Review, Energy.id == Review.energy_id)
        # Левое соединение с таблицей Rating
        .outerjoin(Rating, Review.id == Rating.review_id)
        # Группируем по id бренда
        .group_by(Brand.id)
        # Сортируем
        .order_by(
            # По рейтингу
            desc("average_rating"),
            # По названию бренда
            Brand.name
        )
        # Ограничиваем записи
        .offset(offset)  # Добавляем смещение
        .limit(limit)    # Ограничиваем количество записей
        # Получаем результаты
        .all()
    )

    # Преобразуем результаты
    return [
        # Создаём словарь для бренда
        {
            # Устанавливаем id
            "id": brand_id,
            # Устанавливаем название
            "name": name,
            # Устанавливаем рейтинг
            "average_rating": float(average_rating),
            # Устанавливаем количество энергетиков
            "energy_count": energy_count,
            # Устанавливаем количество отзывов
            "review_count": review_count,
            # Устанавливаем количество оценок
            "rating_count": rating_count,
        }
        # Проходим по результатам
        for brand_id, name, average_rating, energy_count, review_count, rating_count in results
    ]

# =============== READ TOTAL ENERGY COUNT ===============
def get_total_energies(db: Session):
    """
    Возвращает общее количество энергетиков.
    """
    return db.query(Energy).count()

# =============== READ TOTAL BRAND COUNT ===============
def get_total_brands(db: Session):
    """
    Возвращает общее количество брендов.
    """
    return db.query(Brand).count()
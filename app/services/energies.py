# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем функции SQLAlchemy для агрегации и сортировки
from sqlalchemy import func, desc, distinct
# Импортируем модели
from app.db.models import Energy, Review, Rating, Brand, Category
# Импортируем схемы
from app.schemas.energies import Energy as EnergySchema, EnergiesByBrand

# Определяем функцию для получения данных об энергетике
def get_energy(db: Session, energy_id: int):
    # Выполняем запрос для получения энергетика
    result = (
        # Начинаем запрос с таблицы Energy
        db.query(
            # Выбираем объект Energy
            Energy,
            # Вычисляем средний рейтинг
            func.coalesce(func.round(func.avg(Rating.rating_value), 4), 0).label('average_rating'),
            # Считаем количество отзывов
            func.count(distinct(Review.id)).label('review_count')
        )
        # Левое соединение с таблицей Review
        .outerjoin(Review, Energy.id == Review.energy_id)
        # Левое соединение с таблицей Rating
        .outerjoin(Rating, Review.id == Rating.review_id)
        # Фильтруем по energy_id
        .filter(Energy.id == energy_id)
        # Группируем по id энергетика
        .group_by(Energy.id)
        # Получаем первый результат
        .first()
    )
    # Проверяем, есть ли результат
    if result:
        # Распаковываем результат
        energy, avg_rating, review_count = result
        # Устанавливаем средний рейтинг
        energy.average_rating = float(avg_rating) if avg_rating else 0.0
        # Устанавливаем количество отзывов
        energy.review_count = review_count
        # Возвращаем объект энергетика
        return energy
    # Возвращаем None, если энергетик не найден
    return None

# Определяем функцию для получения списка энергетиков
def get_energies(db: Session, skip: int = 0, limit: int = 100):
    # Выполняем запрос к таблице Energy
    query = db.query(Energy)
    # Применяем смещение для пагинации
    query = query.offset(skip)
    # Ограничиваем количество записей
    query = query.limit(limit)
    # Получаем все результаты
    return query.all()

# Определяем функцию для получения энергетиков бренда
def get_energies_by_brand(db: Session, brand_id: int, skip: int = 0, limit: int = 100):
    """
    Получает все энергетики бренда с:
    - Средним рейтингом
    - Количеством отзывов
    - Сортировкой по рейтингу
    Используется в эндпоинте GET /energies/brand/{brand_id}/, доступном всем пользователям.
    """
    # Выполняем запрос для получения энергетиков
    results = (
        # Начинаем запрос с таблицы Energy
        db.query(
            # Выбираем объект Energy
            Energy,
            # Вычисляем средний рейтинг
            func.coalesce(func.round(func.avg(Rating.rating_value), 4), 0).label("average_rating"),
            # Считаем количество отзывов
            func.count(distinct(Review.id)).label("review_count")
        )
        # Фильтруем по brand_id
        .filter(Energy.brand_id == brand_id)
        # Левое соединение с таблицей Review
        .outerjoin(Review, Energy.id == Review.energy_id)
        # Левое соединение с таблицей Rating
        .outerjoin(Rating, Review.id == Rating.review_id)
        # Группируем по id энергетика
        .group_by(Energy.id)
        # Сортируем по рейтингу
        .order_by(desc("average_rating"))
        # Применяем смещение
        .offset(skip)
        # Ограничиваем записи
        .limit(limit)
        # Получаем все результаты
        .all()
    )

    # Преобразуем результаты в список словарей
    return [
        # Создаём словарь для каждого энергетика
        {
            # Распаковываем атрибуты Energy
            **energy.__dict__,
            # Устанавливаем средний рейтинг
            "average_rating": float(average_rating),
            # Устанавливаем количество отзывов
            "review_count": review_count,
            # Устанавливаем бренд
            "brand": energy.brand,
            # Устанавливаем категорию
            "category": energy.category,
        }
        # Проходим по результатам
        for energy, average_rating, review_count in results
    ]
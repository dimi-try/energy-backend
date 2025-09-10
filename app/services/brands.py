from sqlalchemy.orm import Session
from sqlalchemy import func, desc, distinct

from app.db.models import Brand, Energy, Review, Rating

from app.schemas.brands import Brand as BrandSchema, BrandCreate, BrandUpdate

# =============== READ ALL ===============
def get_brands(db: Session, skip: int = 0, limit: int = 10):
    # Выполняем запрос к таблице Brand
    query = db.query(Brand)
    # Применяем смещение для пагинации
    query = query.offset(skip)
    # Ограничиваем количество записей
    query = query.limit(limit)
    # Получаем все результаты
    return query.all()

# =============== READ ONE ===============
def get_brand(db: Session, brand_id: int):
    """
    Получает данные о бренде по его ID, включая:
    - Средний рейтинг (среднее от средних оценок энергетиков)
    - Количество энергетиков
    - Количество энергетиков с оценками
    - Общее количество отзывов
    - Общее количество оценок
    Только энергетики с оценками учитываются в расчете среднего рейтинга.
    Используется в эндпоинте GET /brands/{brand_id}, доступном всем пользователям.
    """
    # Создаём подзапрос для среднего рейтинга энергетиков
    energy_avg_subquery = (
        # Начинаем запрос с таблицы Energy
        db.query(
            # Выбираем brand_id
            Energy.brand_id,
            # Вычисляем средний рейтинг
            func.avg(Rating.rating_value).label("energy_avg_rating")
        )
        # Присоединяем таблицу Review
        .join(Review, Energy.id == Review.energy_id)
        # Присоединяем таблицу Rating
        .join(Rating, Review.id == Rating.review_id)
        # Группируем по id энергетика
        .group_by(Energy.id)
        # Преобразуем в подзапрос
        .subquery()
    )

    # Выполняем основной запрос
    result = (
        # Начинаем запрос с таблицы Brand
        db.query(
            # Выбираем объект Brand
            Brand,
            # Вычисляем средний рейтинг
            func.round(func.avg(energy_avg_subquery.c.energy_avg_rating), 4).label("average_rating"),
            # Считаем количество энергетиков
            func.count(distinct(Energy.id)).label("energy_count"),
            # Считаем количество оцененных энергетиков
            func.count(distinct(energy_avg_subquery.c.energy_avg_rating)).label("rated_energy_count"),
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
        # Фильтруем по brand_id
        .filter(Brand.id == brand_id)
        # Группируем по id бренда
        .group_by(Brand.id)
        # Получаем первый результат
        .first()
    )

    # Проверяем, есть ли результат
    if result:
        # Распаковываем результат
        brand, avg_rating, energy_count, rated_energy_count, review_count, rating_count = result
        # Устанавливаем итоговый рейтинг
        final_rating = round(float(avg_rating), 4) if avg_rating and rated_energy_count > 0 else 0.0
        # Добавляем вычисленные поля
        brand.average_rating = final_rating
        # Устанавливаем количество энергетиков
        brand.energy_count = energy_count or 0
        # Устанавливаем количество оцененных энергетиков
        brand.rated_energy_count = rated_energy_count or 0
        # Устанавливаем количество отзывов
        brand.review_count = review_count or 0
        # Устанавливаем количество оценок
        brand.rating_count = rating_count or 0
        # Возвращаем объект бренда
        return brand
    # Возвращаем None, если бренд не найден
    return None

# =============== READ ALL ENERGIES ONE BRAND===============
def get_energies_by_brand(db: Session, brand_id: int, skip: int = 0, limit: int = 10):
    """
    Получает все энергетики бренда с:
    - Средним рейтингом
    - Количеством отзывов
    - Сортировкой по рейтингу
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

# =============== READ TOTAL ENERGIES COUNT FOR BRAND ===============
def get_total_energies_by_brand(db: Session, brand_id: int):
    """
    Возвращает общее количество энергетиков для указанного бренда.
    """
    return db.query(Energy).filter(Energy.brand_id == brand_id).count()

# =============== ONLY ADMINS ===============

# =============== CREATE ===============
def create_brand(db: Session, brand: BrandCreate):
    """
    Создает новый бренд в базе данных.
    :param db: Сессия базы данных
    :param brand: Данные для создания бренда
    :return: Созданный бренд
    """
    db_brand = Brand(name=brand.name)
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand

# =============== READ ALL ADMIN ===============
def get_brands_admin(db: Session, skip: int = 0, limit: int = 10, search: str = None):
    """
    Получает список всех брендов с пагинацией и поиском по названию бренда.
    """
    query = db.query(Brand)
    
    if search:
        search = search.lower()
        query = query.filter(func.lower(Brand.name).like(f"%{search}%"))
    
    query = query.order_by(Brand.name).offset(skip).limit(limit)
    return query.all()

# =============== UPDATE ===============
def update_brand(db: Session, brand_id: int, brand_update: BrandUpdate):
    """
    Обновляет данные бренда по его ID.
    :param db: Сессия базы данных
    :param brand_id: ID бренда
    :param brand_update: Данные для обновления
    :return: Обновленный бренд или None, если бренд не найден
    """
    db_brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not db_brand:
        return None
    db_brand.name = brand_update.name
    db.commit()
    db.refresh(db_brand)
    return db_brand

# =============== DELETE ===============
def delete_brand(db: Session, brand_id: int):
    """
    Удаляет бренд по его ID.
    :param db: Сессия базы данных
    :param brand_id: ID бренда
    :return: True, если удаление успешно, False, если бренд не найден
    """
    db_brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not db_brand:
        return False
    db.delete(db_brand)
    db.commit()
    return True

# =============== READ ALL FOR SELECT===============
def get_brands_admin_select(db: Session):
    """
    Получает список всех брендов для выбора бренда при создании или изменении энергетика.
    """
    query = db.query(Brand).order_by(Brand.name)
    return query.all()

# =============== READ TOTAL BRANDS COUNT FOR ADMIN ===============
def get_total_brands_admin(db: Session, search: str = None):
    """
    Возвращает общее количество брендов с учетом поиска.
    """
    query = db.query(Brand)
    
    if search:
        search = search.lower()
        query = query.filter(func.lower(Brand.name).like(f"%{search}%"))
    
    return query.count()
# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем функции SQLAlchemy для агрегации и сортировки
from sqlalchemy import func, desc, distinct
# Импортируем модели и схемы из текущего пакета
from . import models, schemas
# Импортируем Dict и Any из typing для аннотации возвращаемых типов
from typing import Dict, Any

# ========================= BRANDS =========================
# Определяем раздел для функций, связанных с брендами

# Функция для получения данных о бренде по его ID
def get_brand(db: Session, brand_id: int):
    """
    Получает данные о бренде по его ID, включая:
    - Средний рейтинг (среднее от средних оценок энергетиков)
    - Количество энергетиков
    - Количество энергетиков с оценками
    - Общее количество отзывов
    - Общее количество оценок
    Только энергетики с оценками учитываются в расчете среднего рейтинга.
    Используется в эндпоинте GET /brand/{brand_id}, доступном всем пользователям.
    """
    # Создаем подзапрос для вычисления среднего рейтинга каждого энергетика бренда
    energy_avg_subquery = (
        # Начинаем запрос с таблицы Energy
        db.query(
            # Выбираем brand_id из таблицы Energy
            models.Energy.brand_id,
            # Вычисляем средний рейтинг для каждого энергетика
            func.avg(models.Rating.rating_value).label("energy_avg_rating")
        )
        # Присоединяем таблицу Review по energy_id
        .join(models.Review, models.Energy.id == models.Review.energy_id)
        # Присоединяем таблицу Rating по review_id
        .join(models.Rating, models.Review.id == models.Rating.review_id)
        # Группируем результаты по id энергетика
        .group_by(models.Energy.id)
        # Преобразуем в подзапрос
        .subquery()
    )

    # Выполняем основной запрос для получения данных о бренде
    result = (
        # Начинаем запрос с таблицы Brand
        db.query(
            # Выбираем объект Brand
            models.Brand,
            # Вычисляем среднее от средних рейтингов энергетиков с округлением до 4 знаков
            func.round(func.avg(energy_avg_subquery.c.energy_avg_rating), 4).label("average_rating"),
            # Считаем общее количество уникальных энергетиков
            func.count(distinct(models.Energy.id)).label("energy_count"),
            # Считаем количество энергетиков с оценками
            func.count(distinct(energy_avg_subquery.c.energy_avg_rating)).label("rated_energy_count"),
            # Считаем общее количество уникальных отзывов
            func.count(distinct(models.Review.id)).label("review_count"),
            # Считаем общее количество уникальных оценок
            func.count(distinct(models.Rating.id)).label("rating_count"),
        )
        # Левое соединение с таблицей Energy по brand_id
        .outerjoin(models.Energy, models.Brand.id == models.Energy.brand_id)
        # Левое соединение с подзапросом по brand_id
        .outerjoin(energy_avg_subquery, models.Brand.id == energy_avg_subquery.c.brand_id)
        # Левое соединение с таблицей Review по energy_id
        .outerjoin(models.Review, models.Energy.id == models.Review.energy_id)
        # Левое соединение с таблицей Rating по review_id
        .outerjoin(models.Rating, models.Review.id == models.Rating.review_id)
        # Фильтруем по указанному brand_id
        .filter(models.Brand.id == brand_id)
        # Группируем результаты по id бренда
        .group_by(models.Brand.id)
        # Получаем первый результат
        .first()
    )

    # Проверяем, есть ли результат
    if result:
        # Распаковываем результат в отдельные переменные
        brand, avg_rating, energy_count, rated_energy_count, review_count, rating_count = result
        
        # Вычисляем итоговый средний рейтинг: если есть рейтинги и оцененные энергетики, округляем, иначе 0
        final_rating = round(float(avg_rating), 4) if avg_rating and rated_energy_count > 0 else 0.0
        
        # Добавляем вычисленные поля в объект бренда
        brand.average_rating = final_rating
        # Устанавливаем количество энергетиков, если нет данных — 0
        brand.energy_count = energy_count or 0
        # Устанавливаем количество оцененных энергетиков, если нет данных — 0
        brand.rated_energy_count = rated_energy_count or 0
        # Устанавливаем количество отзывов, если нет данных — 0
        brand.review_count = review_count or 0
        # Устанавливаем количество оценок, если нет данных — 0
        brand.rating_count = rating_count or 0
        
        # Возвращаем объект бренда с добавленными полями
        return brand
    # Если результата нет, возвращаем None
    return None

# Функция для получения списка всех брендов с пагинацией
def get_brands(db: Session, skip: int = 0, limit: int = 100):
    # Выполняем запрос к таблице Brand
    # Применяем смещение (skip) для пагинации
    # Ограничиваем количество записей (limit)
    # Получаем все результаты
    return db.query(models.Brand).offset(skip).limit(limit).all()

# ========================= ENERGIES =========================
# Определяем раздел для функций, связанных с энергетиками

# Функция для получения данных об энергетике по его ID
def get_energy(db: Session, energy_id: int):
    # Выполняем запрос для получения данных об энергетике
    result = (
        db.query(
            # Выбираем объект Energy
            models.Energy,
            # Вычисляем средний рейтинг энергетика с округлением до 4 знаков, если нет данных — 0
            func.coalesce(func.round(func.avg(models.Rating.rating_value), 4), 0).label('average_rating'),
            # Считаем количество отзывов
            func.count(distinct(models.Review.id)).label('review_count')
        )
        # Левое соединение с таблицей Review по energy_id
        .outerjoin(models.Review, models.Energy.id == models.Review.energy_id)\
        # Левое соединение с таблицей Rating по review_id
        .outerjoin(models.Rating, models.Review.id == models.Rating.review_id)\
        # Фильтруем по указанному energy_id
        .filter(models.Energy.id == energy_id)\
        # Группируем результаты по id энергетика
        .group_by(models.Energy.id)\
        # Получаем первый результат
        .first()
    )
    # Проверяем, есть ли результат
    if result:
        # Распаковываем результат в объект энергетика и средний рейтинг
        energy, avg_rating, review_count = result
        # Добавляем средний рейтинг в объект, преобразуем в float, если None — 0
        energy.average_rating = float(avg_rating) if avg_rating else 0.0
        # Добавляем количество отзывов
        energy.review_count = review_count
        # Возвращаем объект энергетика
        return energy
    # Если результата нет, возвращаем None
    return None

# Функция для получения списка всех энергетиков с пагинацией
def get_energies(db: Session, skip: int = 0, limit: int = 100):
    # Выполняем запрос к таблице Energy
    # Применяем смещение (skip) для пагинации
    # Ограничиваем количество записей (limit)
    # Получаем все результаты
    return db.query(models.Energy).offset(skip).limit(limit).all()

# Функция для получения списка энергетиков определенного бренда
def get_energies_by_brand(db: Session, brand_id: int, skip: int = 0, limit: int = 100):
    """
    Получает все энергетики бренда с:
    - Средним рейтингом
    - Количеством отзывов
    - Сортировкой по рейтингу
    Используется в эндпоинте GET /brands/{brand_id}/energies/, доступном всем пользователям.
    """
    # Выполняем запрос для получения энергетиков бренда
    results = (
        # Начинаем запрос с таблицы Energy
        db.query(
            # Выбираем объект Energy
            models.Energy,
            # Вычисляем средний рейтинг энергетика, если нет данных — 0
            func.coalesce(func.round(func.avg(models.Rating.rating_value), 4), 0).label("average_rating"),
            # Считаем количество уникальных отзывов для энергетика
            func.count(distinct(models.Review.id)).label("review_count")
        )
        # Фильтруем по указанному brand_id
        .filter(models.Energy.brand_id == brand_id)
        # Левое соединение с таблицей Review по energy_id
        .outerjoin(models.Review, models.Energy.id == models.Review.energy_id)
        # Левое соединение с таблицей Rating по review_id
        .outerjoin(models.Rating, models.Review.id == models.Rating.review_id)
        # Группируем результаты по id энергетика
        .group_by(models.Energy.id)
        # Сортируем по убыванию среднего рейтинга
        .order_by(desc("average_rating"))
        # Применяем смещение (skip) для пагинации
        .offset(skip)
        # Ограничиваем количество записей (limit)
        .limit(limit)
        # Получаем все результаты
        .all()
    )

    # Преобразуем результаты в список словарей с нужными полями
    return [
        # Создаем словарь для каждого энергетика
        {
            # Распаковываем все атрибуты объекта Energy
            **energy.__dict__,
            # Добавляем средний рейтинг, преобразуем в float
            "average_rating": float(average_rating),
            # Добавляем количество отзывов
            "review_count": review_count,
            # Добавляем объект бренда
            "brand": energy.brand,
            # Добавляем объект категории (может быть None)
            "category": energy.category,
        }
        # Проходим по каждому кортежу из результатов
        for energy, average_rating, review_count in results
    ]

# ========================= USERS =========================
# Определяем раздел для функций, связанных с пользователями

# Функция для получения данных о пользователе по его ID
def get_user(db: Session, user_id: int):
    # Выполняем запрос к таблице User
    # Фильтруем по указанному user_id
    # Получаем первый результат
    return db.query(models.User).filter(models.User.id == user_id).first()

# Функция для получения данных о пользователе по его email
def get_user_by_email(db: Session, email: str):
    # Выполняем запрос к таблице User
    # Фильтруем по указанному email
    # Получаем первый результат
    return db.query(models.User).filter(models.User.email == email).first()

# Функция для создания нового пользователя
def create_user(db: Session, user: schemas.UserCreate):
    # Создаем новый объект User с данными из схемы
    db_user = models.User(
        # Устанавливаем имя пользователя
        username=user.username,
        # Устанавливаем email
        email=user.email,
        # Устанавливаем пароль (без хеширования — нужно добавить!)
        password=user.password  # В реальном приложении необходимо хеширование!
    )
    # Добавляем объект в сессию базы данных
    db.add(db_user)
    # Фиксируем изменения в базе данных
    db.commit()
    # Обновляем объект данными из базы (например, id)
    db.refresh(db_user)
    # Возвращаем созданный объект пользователя
    return db_user

# Функция для проверки, оставил ли пользователь отзыв на энергетик
def get_review_by_user_and_energy(db: Session, user_id: int, energy_id: int):
    # Выполняем запрос к таблице Review
    # Фильтруем по user_id и energy_id
    # Получаем первый результат
    return db.query(models.Review).filter(
        models.Review.user_id == user_id,
        models.Review.energy_id == energy_id
    ).first()

# ========================= REVIEWS & RATINGS =========================
# Определяем раздел для функций, связанных с отзывами и оценками

# Функция для создания отзыва с оценками
def create_review_with_ratings(db: Session, review: schemas.ReviewCreate):
    # Создаем новый объект Review с данными из схемы
    db_review = models.Review(
        # Устанавливаем идентификатор пользователя
        user_id=review.user_id,
        # Устанавливаем идентификатор энергетика
        energy_id=review.energy_id,
        # Устанавливаем текст отзыва
        review_text=review.review_text
    )
    # Добавляем объект в сессию базы данных
    db.add(db_review)
    # Фиксируем изменения в базе данных
    db.commit()
    # Обновляем объект данными из базы (например, id)
    db.refresh(db_review)
    
    # Проходим по списку оценок из схемы
    for rating in review.ratings:
        # Создаем новый объект Rating для каждой оценки
        db_rating = models.Rating(
            # Устанавливаем идентификатор отзыва
            review_id=db_review.id,
            # Устанавливаем идентификатор критерия
            criteria_id=rating.criteria_id,
            # Устанавливаем значение оценки
            rating_value=rating.rating_value
        )
        # Добавляем объект в сессию базы данных
        db.add(db_rating)
    
    # Фиксируем все изменения в базе данных
    db.commit()
    # Возвращаем созданный объект отзыва
    return db_review

# Функция для получения данных об отзыве по его ID
def get_review(db: Session, review_id: int):
    # Выполняем запрос к таблице Review
    # Фильтруем по указанному review_id
    # Получаем первый результат
    return db.query(models.Review).filter(models.Review.id == review_id).first()

# Функция для получения списка отзывов на энергетик с пагинацией
def get_reviews_by_energy(db: Session, energy_id: int, skip: int = 0, limit: int = 100):
    # Выполняем запрос к таблице Review
    # Фильтруем по указанному energy_id
    # Применяем смещение (skip) для пагинации
    # Ограничиваем количество записей (limit)
    # Получаем все результаты
    return db.query(models.Review).filter(models.Review.energy_id == energy_id).offset(skip).limit(limit).all()

# Функция для получения данных об оценке по ее ID
def get_rating(db: Session, rating_id: int):
    # Выполняем запрос к таблице Rating
    # Фильтруем по указанному rating_id
    # Получаем первый результат
    return db.query(models.Rating).filter(models.Rating.id == rating_id).first()

# Функция для получения списка оценок для отзыва
def get_ratings_by_review(db: Session, review_id: int):
    # Выполняем запрос к таблице Rating
    # Фильтруем по указанному review_id
    # Получаем все результаты
    return db.query(models.Rating).filter(models.Rating.review_id == review_id).all()

# ========================= CRITERIA =========================
# Определяем раздел для функций, связанных с критериями

# Функция для создания нового критерия
def create_criteria(db: Session, criteria: schemas.CriteriaCreate):
    # Создаем новый объект Criteria с данными из схемы
    db_criteria = models.Criteria(name=criteria.name)
    # Добавляем объект в сессию базы данных
    db.add(db_criteria)
    # Фиксируем изменения в базе данных
    db.commit()
    # Обновляем объект данными из базы (например, id)
    db.refresh(db_criteria)
    # Возвращаем созданный объект критерия
    return db_criteria

# Функция для получения критерия по его названию
def get_criteria_by_name(db: Session, name: str):
    # Выполняем запрос к таблице Criteria
    # Фильтруем по указанному name
    # Получаем первый результат
    return db.query(models.Criteria).filter(models.Criteria.name == name).first()

# Функция для получения списка всех критериев с пагинацией
def get_all_criteria(db: Session, skip: int = 0, limit: int = 100):
    # Выполняем запрос к таблице Criteria
    # Применяем смещение (skip) для пагинации
    # Ограничиваем количество записей (limit)
    # Получаем все результаты
    return db.query(models.Criteria).offset(skip).limit(limit).all()

# ========================= CATEGORIES =========================
# Определяем раздел для функций, связанных с категориями

# Функция для создания новой категории
def create_category(db: Session, category: schemas.CategoryCreate):
    # Создаем новый объект Category с данными из схемы
    db_category = models.Category(name=category.name)
    # Добавляем объект в сессию базы данных
    db.add(db_category)
    # Фиксируем изменения в базе данных
    db.commit()
    # Обновляем объект данными из базы (например, id)
    db.refresh(db_category)
    # Возвращаем созданный объект категории
    return db_category

# Функция для получения категории по ее названию
def get_category_by_name(db: Session, name: str):
    # Выполняем запрос к таблице Category
    # Фильтруем по указанному name
    # Получаем первый результат
    return db.query(models.Category).filter(models.Category.name == name).first()

# Функция для получения списка всех категорий с пагинацией
def get_categories(db: Session, skip: int = 0, limit: int = 100):
    # Выполняем запрос к таблице Category
    # Применяем смещение (skip) для пагинации
    # Ограничиваем количество записей (limit)
    # Получаем все результаты
    return db.query(models.Category).offset(skip).limit(limit).all()

# ========================= USER PROFILE =========================
# Определяем раздел для функции профиля пользователя

# Функция для получения профиля пользователя
def get_user_profile(db: Session, user_id: int) -> Dict[str, Any]:
    # Получаем объект пользователя по его ID
    user = db.query(models.User).get(user_id)
    # Проверяем, существует ли пользователь
    if not user:
        # Если пользователя нет, возвращаем None
        return None

    # Получаем все отзывы пользователя
    reviews = db.query(models.Review).filter(models.Review.user_id == user_id).all()
    # Считаем общее количество отзывов
    total_rated = len(reviews)
    
    # Проверяем, есть ли отзывы
    if total_rated == 0:
        # Если отзывов нет, возвращаем базовый профиль без статистики
        return {
            "user": user,
            "total_ratings": 0,
            "average_rating": None,
            "favorite_brand": None,
            "favorite_energy": None
        }

    # Инициализируем переменные для расчета статистики
    total_rating = 0
    # Словарь для статистики по брендам
    brand_stats = {}
    # Словарь для статистики по энергетикам
    energy_stats = {}

    # Проходим по всем отзывам пользователя
    for review in reviews:
        # Получаем все оценки для данного отзыва
        ratings = db.query(models.Rating).filter(models.Rating.review_id == review.id).all()
        # Проходим по всем оценкам
        for rating in ratings:
            # Добавляем значение оценки к общей сумме
            total_rating += rating.rating_value
            
            # Получаем объект энергетика для отзыва
            energy = db.query(models.Energy).get(review.energy_id)
            # Получаем идентификатор бренда
            brand_id = energy.brand_id
            # Добавляем оценку в статистику бренда
            brand_stats[brand_id] = brand_stats.get(brand_id, 0) + rating.rating_value
            
            # Добавляем оценку в статистику энергетика
            energy_stats[review.energy_id] = energy_stats.get(review.energy_id, 0) + rating.rating_value

    # Вычисляем средний рейтинг: общая сумма оценок делится на количество отзывов и критериев
    average_rating = total_rating / (total_rated * len(db.query(models.Criteria).all()))

    # Определяем любимый бренд: бренд с максимальной суммой оценок
    favorite_brand_id = max(brand_stats, key=brand_stats.get) if brand_stats else None
    # Получаем объект любимого бренда, если он есть
    favorite_brand = db.query(models.Brand).get(favorite_brand_id) if favorite_brand_id else None

    # Определяем любимый энергетик: энергетик с максимальной суммой оценок
    favorite_energy_id = max(energy_stats, key=energy_stats.get) if energy_stats else None
    # Получаем объект любимого энергетика, если он есть
    favorite_energy = db.query(models.Energy).get(favorite_energy_id) if favorite_energy_id else None

    # Возвращаем профиль пользователя со статистикой
    return {
        "user": user,
        "total_ratings": total_rated,
        "average_rating": round(average_rating, 1),
        "favorite_brand": favorite_brand,
        "favorite_energy": favorite_energy
    }

# ========================= TOP RATINGS =========================
# Определяем раздел для функций топов

# Функция для получения топа энергетиков
def get_top_energies(db: Session, limit: int = 100):
    # Создаем подзапрос для вычисления среднего рейтинга каждого энергетика
    avg_rating_subquery = (
        # Начинаем запрос с таблицы Review
        db.query(
            # Выбираем energy_id из таблицы Review
            models.Review.energy_id,
            # Вычисляем средний рейтинг с округлением до 4 знаков
            func.round(func.avg(models.Rating.rating_value), 4).label('avg_rating')
        )
        # Присоединяем таблицу Rating по review_id
        .join(models.Rating)
        # Группируем результаты по energy_id
        .group_by(models.Review.energy_id)
        # Преобразуем в подзапрос
        .subquery()
    )

    # Создаем подзапрос для вычисления количества отзывов для каждого энергетика
    review_count_subquery = (
        # Начинаем запрос с таблицы Review
        db.query(
            # Выбираем energy_id из таблицы Review
            models.Review.energy_id,
            # Считаем количество отзывов
            func.count(models.Review.id).label('review_count')
        )
        # Группируем результаты по energy_id
        .group_by(models.Review.energy_id)
        # Преобразуем в подзапрос
        .subquery()
    )

    # Выполняем основной запрос для получения топа энергетиков
    energies = (
        # Начинаем запрос с таблицы Energy
        db.query(
            # Выбираем объект Energy
            models.Energy,
            # Используем средний рейтинг из подзапроса, если нет данных — 0
            func.coalesce(avg_rating_subquery.c.avg_rating, 0).label('average_rating'),
            # Используем количество отзывов из подзапроса, если нет данных — 0
            func.coalesce(review_count_subquery.c.review_count, 0).label('review_count')
        )
        # Левое соединение с подзапросом среднего рейтинга по energy_id
        .outerjoin(avg_rating_subquery, models.Energy.id == avg_rating_subquery.c.energy_id)
        # Левое соединение с подзапросом количества отзывов по energy_id
        .outerjoin(review_count_subquery, models.Energy.id == review_count_subquery.c.energy_id)
        # Присоединяем таблицу Brand для сортировки
        .join(models.Brand)
        # Сортируем результаты
        .order_by(
            # Сначала по убыванию среднего рейтинга
            desc('average_rating'),
            # Затем по убыванию количества отзывов
            desc('review_count'),
            # Затем по названию бренда
            models.Brand.name,
            # Затем по названию энергетика
            models.Energy.name
        )
        # Ограничиваем количество записей
        .limit(limit)
        # Получаем все результаты
        .all()
    )

    # Преобразуем результаты в список словарей
    return [{
        # Устанавливаем id энергетика
        "id": energy.id,
        # Устанавливаем название энергетика
        "name": energy.name,
        # Устанавливаем средний рейтинг, преобразуем в float
        "average_rating": float(avg_rating),
        # Устанавливаем объект бренда
        "brand": energy.brand,
        # Устанавливаем объект категории (может быть None)
        "category": energy.category,
        # Устанавливаем количество отзывов
        "review_count": review_count
    # Проходим по каждому кортежу из результатов
    } for energy, avg_rating, review_count in energies]

# Функция для получения топа брендов
def get_top_brands(db: Session, limit: int = 100):
    """
    Получает топ брендов с:
    - Средним рейтингом (правильный расчет)
    - Количеством энергетиков
    - Количеством отзывов
    - Количеством оценок
    - Сортировкой по рейтингу
    Используется в эндпоинте GET /top/brands/, доступном всем пользователям.
    """
    # Создаем подзапрос для средних рейтингов энергетиков
    energy_avg_subquery = (
        # Начинаем запрос с таблицы Energy
        db.query(
            # Выбираем brand_id из таблицы Energy
            models.Energy.brand_id,
            # Вычисляем средний рейтинг для каждого энергетика
            func.avg(models.Rating.rating_value).label("energy_avg_rating"),
        )
        # Левое соединение с таблицей Review по energy_id
        .outerjoin(models.Review, models.Energy.id == models.Review.energy_id)
        # Левое соединение с таблицей Rating по review_id
        .outerjoin(models.Rating, models.Review.id == models.Rating.review_id)
        # Группируем результаты по id энергетика
        .group_by(models.Energy.id)
        # Преобразуем в подзапрос
        .subquery()
    )

    # Выполняем основной запрос для получения топа брендов
    results = (
        # Начинаем запрос с таблицы Brand
        db.query(
            # Выбираем id бренда
            models.Brand.id,
            # Выбираем название бренда
            models.Brand.name,
            # Вычисляем средний рейтинг бренда с округлением, если нет данных — 0
            func.coalesce(func.round(func.avg(energy_avg_subquery.c.energy_avg_rating), 4), 0).label("average_rating"),
            # Считаем количество уникальных энергетиков
            func.count(distinct(models.Energy.id)).label("energy_count"),
            # Считаем количество уникальных отзывов
            func.count(distinct(models.Review.id)).label("review_count"),
            # Считаем количество уникальных оценок
            func.count(distinct(models.Rating.id)).label("rating_count"),
        )
        # Левое соединение с таблицей Energy по brand_id
        .outerjoin(models.Energy, models.Brand.id == models.Energy.brand_id)
        # Левое соединение с подзапросом по brand_id
        .outerjoin(energy_avg_subquery, models.Brand.id == energy_avg_subquery.c.brand_id)
        # Левое соединение с таблицей Review по energy_id
        .outerjoin(models.Review, models.Energy.id == models.Review.energy_id)
        # Левое соединение с таблицей Rating по review_id
        .outerjoin(models.Rating, models.Review.id == models.Rating.review_id)
        # Группируем результаты по id бренда
        .group_by(models.Brand.id)
        # Сортируем по убыванию среднего рейтинга
        .order_by(desc("average_rating"))
        # Ограничиваем количество записей
        .limit(limit)
        # Получаем все результаты
        .all()
    )

    # Преобразуем результаты в список словарей
    return [
        # Создаем словарь для каждого бренда
        {
            # Устанавливаем id бренда
            "id": brand_id,
            # Устанавливаем название бренда
            "name": name,
            # Устанавливаем средний рейтинг, преобразуем в float
            "average_rating": float(average_rating),
            # Устанавливаем количество энергетиков
            "energy_count": energy_count,
            # Устанавливаем количество отзывов
            "review_count": review_count,
            # Устанавливаем количество оценок
            "rating_count": rating_count,
        }
        # Проходим по каждому кортежу из результатов
        for brand_id, name, average_rating, energy_count, review_count, rating_count in results
    ]
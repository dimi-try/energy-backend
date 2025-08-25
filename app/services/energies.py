from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
import os

from app.db.models import Energy, Review, Rating, Brand, Category

from app.schemas.energies import EnergyCreate, EnergyUpdate

# =============== READ ALL ===============
def get_energies(db: Session, skip: int = 0, limit: int = 100):
    # Выполняем запрос к таблице Energy
    query = db.query(Energy)
    # Применяем смещение для пагинации
    query = query.offset(skip)
    # Ограничиваем количество записей
    query = query.limit(limit)
    # Получаем все результаты
    return query.all()

# =============== READ ONE ===============
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

# =============== READ ALL REVIEWS ONE ENERGY ===============
def get_reviews_by_energy(db: Session, energy_id: int, skip: int = 0, limit: int = 10):
    # Выполняем запрос к таблице Review с фильтрацией и сортировкой
    query = (
        db.query(Review) # Выполняем запрос к таблице Review
        .filter(Review.energy_id == energy_id) # Фильтруем по energy_id
        .order_by(Review.created_at.desc())  # сортировка по убыванию (сначала новые)
        .offset(skip) # Применяем смещение
        .limit(limit) # Ограничиваем записи
    )

    # Получаем все результаты
    result = query.all()

    # Проверяем, есть ли результаты
    if not result:
        return []  
    # Добавляем средний рейтинг к каждому отзыву
    for review in result:   
        # Выполняем запрос к таблице Rating для получения среднего рейтинга
        avg_rating = (
            db.query(func.avg(Rating.rating_value))
            .filter(Rating.review_id == review.id)
            .scalar()
        )
        # Устанавливаем средний рейтинг в отзыв
        review.average_rating_review = round(float(avg_rating), 4) if avg_rating else 0.0
    # Возвращаем список отзывов с установленным средним рейтингом
    return result
    
# =============== READ TOTAL REVIEWS COUNT FOR ENERGY ===============
def get_total_reviews_by_energy(db: Session, energy_id: int):
    """
    Возвращает общее количество отзывов для указанного энергетика.
    """
    return db.query(Review).filter(Review.energy_id == energy_id).count()

# =============== ONLY ADMINS ===============

# =============== CREATE ===============
def create_energy(db: Session, energy: EnergyCreate):
    """
    Создает новый энергетик в базе данных.
    """
    db_energy = Energy(
        name=energy.name,
        brand_id=energy.brand_id,
        category_id=energy.category_id,
        description=energy.description,
        ingredients=energy.ingredients,
        image_url=energy.image_url
    )
    db.add(db_energy)
    db.commit()
    db.refresh(db_energy)
    return db_energy

# =============== READ ALL WITHOUT PAGINATION ===============
def get_energies_admin(db: Session):
    # Выполняем запрос к таблице Energy
    query = db.query(Energy)
    # Получаем все результаты
    return query.all()

# =============== UPDATE ===============
def update_energy(db: Session, energy_id: int, energy_update: EnergyUpdate):
    """
    Обновляет данные энергетика по его ID.
    """
    db_energy = db.query(Energy).filter(Energy.id == energy_id).first()
    if not db_energy:
        return None
    update_data = energy_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_energy, key, value)
    db.commit()
    db.refresh(db_energy)
    return db_energy

# =============== DELETE ===============
def delete_energy(db: Session, energy_id: int):
    """
    Удаляет энергетик по его ID.
    """
    db_energy = db.query(Energy).filter(Energy.id == energy_id).first()
    if not db_energy:
        return False
    # Удаляем файл
    if db_energy.image_url and os.path.exists(db_energy.image_url):
        os.remove(db_energy.image_url)  
    db.delete(db_energy)
    db.commit()
    return True
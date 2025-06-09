# Импортируем Session из SQLAlchemy для работы с базой данных
from sqlalchemy.orm import Session
# Импортируем модели
from app.db.models import Criteria
# Импортируем схемы
from app.schemas.criteria import CriteriaCreate

# Определяем функцию для создания критерия
def create_criteria(db: Session, criteria: CriteriaCreate):
    # Создаём объект Criteria
    db_criteria = Criteria(name=criteria.name)
    # Добавляем в сессию
    db.add(db_criteria)
    # Фиксируем изменения
    db.commit()
    # Обновляем объект
    db.refresh(db_criteria)
    # Возвращаем критерий
    return db_criteria

# Определяем функцию для получения критерия по имени
def get_criteria_by_name(db: Session, name: str):
    # Выполняем запрос к таблице Criteria
    query = db.query(Criteria)
    # Фильтруем по имени
    query = query.filter(Criteria.name == name)
    # Получаем первый результат
    return query.first()

# Определяем функцию для получения всех критериев
def get_all_criteria(db: Session, skip: int = 0, limit: int = 100):
    # Выполняем запрос к таблице Criteria
    query = db.query(Criteria)
    # Применяем смещение
    query = query.offset(skip)
    # Ограничиваем записи
    query = query.limit(limit)
    # Получаем все результаты
    return query.all()
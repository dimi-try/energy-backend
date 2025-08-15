from sqlalchemy.orm import Session

from app.db.models import Criteria

from app.schemas.criteria import CriteriaUpdate

# =============== READ ALL ===============
def get_all_criteria(db: Session, skip: int = 0, limit: int = 100):
    # Выполняем запрос к таблице Criteria
    query = db.query(Criteria)
    # Применяем смещение
    query = query.offset(skip)
    # Ограничиваем записи
    query = query.limit(limit)
    # Получаем все результаты
    return query.all()

# =============== ONLY ADMINS ===============

# =============== READ ONE CRITERIA BY NAME ===============
def get_criteria_by_name(db: Session, name: str):
    # Выполняем запрос к таблице Criteria
    query = db.query(Criteria)
    # Фильтруем по имени
    query = query.filter(Criteria.name == name)
    # Получаем первый результат
    return query.first()

# =============== UPDATE ===============
def update_criteria(db: Session, criteria_id: int, criteria_update: CriteriaUpdate):
    """
    Обновляет данные критерия по его ID.
    """
    db_criteria = db.query(Criteria).filter(Criteria.id == criteria_id).first()
    if not db_criteria:
        return None
    if criteria_update.name:  # Проверяем, указано ли новое имя
        existing_criteria = get_criteria_by_name(db, criteria_update.name)
        if existing_criteria and existing_criteria.id != criteria_id:
            raise ValueError("Критерий с таким именем уже существует")
        db_criteria.name = criteria_update.name
    db.commit()
    db.refresh(db_criteria)
    return db_criteria
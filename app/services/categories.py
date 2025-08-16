from sqlalchemy.orm import Session

from app.db.models import Category

from app.schemas.categories import CategoryCreate, CategoryUpdate

# =============== READ ALL ===============
def get_categories(db: Session, skip: int = 0, limit: int = 100):
    # Выполняем запрос к таблице Category
    query = db.query(Category)
    # Применяем смещение
    query = query.offset(skip)
    # Ограничиваем записи
    query = query.limit(limit)
    # Получаем все результаты
    return query.all()

# =============== ONLY ADMINS ===============

# =============== CREATE ===============
def create_category(db: Session, category: CategoryCreate):
    # Создаём объект Category
    db_category = Category(name=category.name)
    # Добавляем в сессию
    db.add(db_category)
    # Фиксируем изменения
    db.commit()
    # Обновляем объект
    db.refresh(db_category)
    # Возвращаем категорию
    return db_category

# =============== READ ALL WITHOUT PAGINATION ===============
def get_categories_admin(db: Session):
    # Выполняем запрос к таблице Category
    query = db.query(Category)
    # Получаем все результаты
    return query.all()

# =============== READ ONE CATEGORY BY NAME ===============
def get_category_by_name(db: Session, name: str):
    # Выполняем запрос к таблице Category
    query = db.query(Category)
    # Фильтруем по имени
    query = query.filter(Category.name == name)
    # Получаем первый результат
    return query.first()

# =============== UPDATE ===============
def update_category(db: Session, category_id: int, category_update: CategoryUpdate):
    """
    Обновляет данные категории по его ID.
    """
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        return None
    if category_update.name:  # Проверяем, указано ли новое имя
        existing_category = get_category_by_name(db, category_update.name)
        if existing_category and existing_category.id != category_id:
            raise ValueError("Категория с таким именем уже существует")
        db_category.name = category_update.name
    db.commit()
    db.refresh(db_category)
    return db_category
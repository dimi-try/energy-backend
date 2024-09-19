from sqlalchemy.orm import Session
from . import models, schemas

# ЗДЕСЬ ПРОИСХОДИТ ВЗАИМОДЕЙСТВИЕ С БАЗОЙ ДАННЫХ

# ===================== CRUD ОППЕРАЦИИ С ТАБЛИЦЕЙ BRAND =====================

# Функция получения элемента по его id
def get_brand(db: Session, brand_id: int):
    return db.query(models.Brand).filter(models.Brand.id == brand_id).first()

# Функция создания элемента
# def create_brand(db: Session, brand: schemas.BrandCreate):
#     db_brand = models.Brand(name=brand.name, description=brand.description)
#     db.add(db_brand)
#     db.commit()
#     db.refresh(db_brand)
#     return db_brand

# ===================== CRUD ОППЕРАЦИИ С ТАБЛИЦЕЙ ENERGY =====================

def get_energy(db: Session, energy_id: int):
    return db.query(models.Energy).filter(models.Energy.id == energy_id).first()

# Создание нового энергетика
def create_energy(db: Session, energy: schemas.EnergyCreate):
    db_energy = models.Energy(
        name=energy.name,
        brand_id=energy.brand_id,
        description=energy.description
    )
    db.add(db_energy)
    db.commit()
    db.refresh(db_energy)
    return db_energy


# ЕПТ! ТУТ УЖЕ НАСТРОЕНА ПАГИНАЦИЯ!?!?
#GET /energy/ — получить список энергетиков с возможностью пагинации (параметры skip и limit).
# Получение всех энергетиков
def get_energies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Energy).offset(skip).limit(limit).all()
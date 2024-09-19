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

def get_energy(db: Session, brand_id: int):
    return db.query(models.Brand).filter(models.Brand.id == brand_id).first()
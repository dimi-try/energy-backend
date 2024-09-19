from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine

router = APIRouter()

# Создаем таблицы в базе данных
models.Base.metadata.create_all(bind=engine)

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========================= BRAND ENDPOINTS =========================

# Пока что энедпоинты создания и изменения не поддерживаются

# @router.post("/brands/", response_model=schemas.Brand)
# def create_brand(brand: schemas.BrandCreate, db: Session = Depends(get_db)):
#     return crud.create_brand(db=db, brand=brand)

@router.get("/brands/{brand_id}", response_model=schemas.Brand)
def read_brand(brand_id: int, db: Session = Depends(get_db)):
    db_brand = crud.get_brand(db, brand_id=brand_id)
    if db_brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return db_brand

# ========================= ENERGY ENDPOINTS =========================

# Пока что энедпоинты создания и изменения не поддерживаются

# @app.post("/energy/", response_model=schemas.Energy)
# def create_energy(energy: schemas.EnergyCreate, db: Session = Depends(get_db)):
#     db_energy = models.Energy(**energy.dict())
#     db.add(db_energy)
#     db.commit()
#     db.refresh(db_energy)
#     return db_energy

@router.get("/energy/{energy_id}", response_model=schemas.Energy)
def read_energy(energy_id: int, db: Session = Depends(get_db)):
    db_energy = db.query(models.Energy).filter(models.Energy.id == energy_id).first()
    if db_energy is None:
        raise HTTPException(status_code=404, detail="Energy not found")
    
    # Получение бренда для указанного energy
    brand = db.query(models.Brand).filter(models.Brand.id == db_energy.brand_id).first()
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")

    # Создание объекта для возвращаемого результата
    return schemas.Energy(
        id=db_energy.id,
        name=db_energy.name,
        brand=schemas.Brand.from_orm(brand),
        description=db_energy.description
    )

# @router.get("/energy/{energy_id}", response_model=schemas.Energy)
# def read_energy(energy_id: int, db: Session = Depends(get_db)):
#     db_energy = db.query(models.Energy).filter(models.Energy.id == energy_id).first()
#     if db_energy is None:
#         raise HTTPException(status_code=404, detail="Energy not found")

#     brand = db.query(models.Brand).filter(models.Brand.id == db_energy.brand_id).first()
#     if brand is None:
#         raise HTTPException(status_code=404, detail="Brand not found")

#     # Передаем данные в Pydantic схему с использованием from_orm
#     return schemas.Energy(
#         id=db_energy.id,
#         name=db_energy.name,
#         brand=schemas.Brand.from_orm(brand),  # Используем from_orm для преобразования
#         description=db_energy.description
#     )
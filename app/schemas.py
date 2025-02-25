from pydantic import BaseModel, constr
from typing import Optional


# =============== БРЕНДЫ ===============
class BrandBase(BaseModel):
    name: constr(max_length=64)

class BrandCreate(BrandBase):
    pass

class Brand(BrandBase):
    id: int

    class Config:
        from_attributes = True

# =============== ЭНЕРГЕТИКИ ===============
class EnergyBase(BaseModel):
    name: constr(max_length=64)
    description: Optional[str] = None

# Схема для создания новой записи
class EnergyCreate(EnergyBase):
    brand_id: int

# Схема для представления данных
class Energy(EnergyBase):
    id: int
    brand: Brand

    class Config:
        from_attributes = True

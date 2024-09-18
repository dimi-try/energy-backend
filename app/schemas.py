from pydantic import BaseModel
from typing import Optional

class BrandModel(BaseModel):
    id: int
    name: str

class EnergeticModel(BaseModel):
    id: int
    name: Optional[str]
    brand: BrandModel
    rating: float

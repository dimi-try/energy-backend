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

class RatingModel(BaseModel):
    id: int
    user_id: int
    energy_id: int
    rating: Optional[float]
    review: Optional[str]
    criteria_id: Optional[int]
    created_at: Optional[str]
    is_history: bool
    original_rating_id: Optional[int]

class UserModel(BaseModel):
    id: int
    name: str
    email: str
    created_at: str

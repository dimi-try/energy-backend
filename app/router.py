from fastapi import APIRouter, Depends
from app.repository import EnergeticRepository
from app.schemas import EnergeticModel
from typing import List

api_router = APIRouter()

@api_router.get("/api/energetics", response_model=List[EnergeticModel])
async def get_energetics():
    return await EnergeticRepository.get_all()

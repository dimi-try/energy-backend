from fastapi import APIRouter, Request, Depends, HTTPException, Path
from app.repository import EnergeticRepository, RatingRepository, BrandRepository, UserRepository
from app.schemas import EnergeticModel, RatingModel, BrandModel, UserModel
from app.auth import create_access_token, verify_token, validate
from typing import List
import time
import urllib.parse

api_router = APIRouter()

@api_router.post("/auth/verify")
async def authorization_test(request: Request):
    authorization_data = await request.json()
    parsed_query = urllib.parse.parse_qs(authorization_data)
    hash_received = parsed_query.get('hash', [None])[0]
    auth_date = int(parsed_query.get('auth_date', [0])[0])

    if not hash_received:
        raise HTTPException(status_code=400, detail="Hash not provided")

    if validate(hash_received, authorization_data):
        current_unix_time = int(time.time())
        timeout_seconds = 3600
        if current_unix_time - auth_date > timeout_seconds:
            raise HTTPException(status_code=403, detail="Verification failed due to timeout")
        
        access_token = create_access_token({"sub": "user_id"}, expires_delta=3600)
        return {"success": True, "message": "Verification successful", "access_token": access_token}
    else:
        raise HTTPException(status_code=403, detail="Verification failed")


@api_router.get("/auth/protected")
async def protected_endpoint(token: str = Depends(verify_token)):
    return {"message": "Protected content", "user_data": token}

@api_router.get("/api/energetics", response_model=List[EnergeticModel])
async def get_energetics():
    return await EnergeticRepository.get_all()

@api_router.post("/api/ratings")
async def add_rating(rating: RatingModel, token: str = Depends(verify_token)):
    user_id = token["sub"]
    await RatingRepository.add_rating(user_id, rating)
    return {"success": True, "message": "Rating added"}

@api_router.put("/api/ratings/{rating_id}")
async def update_rating(rating_id: int, rating: RatingModel, token: str = Depends(verify_token)):
    user_id = token["sub"]
    await RatingRepository.update_rating(rating_id, user_id, rating)
    return {"success": True, "message": "Rating updated"}

@api_router.delete("/api/ratings/{rating_id}")
async def delete_rating(rating_id: int, token: str = Depends(verify_token)):
    user_id = token["sub"]
    await RatingRepository.delete_rating(rating_id, user_id)
    return {"success": True, "message": "Rating deleted"}

@api_router.get("/api/ratings/{energy_id}", response_model=List[RatingModel])
async def get_ratings_by_energy(energy_id: int):
    return await RatingRepository.get_ratings_by_energy(energy_id)

@api_router.get("/api/ratings/user/{user_id}", response_model=List[RatingModel])
async def get_ratings_by_user(user_id: int):
    return await RatingRepository.get_ratings_by_user(user_id)

@api_router.get("/api/brands", response_model=List[BrandModel])
async def get_brands():
    return await BrandRepository.get_all()

@api_router.get("/api/brand/{brand_id}/energetics", response_model=List[EnergeticModel])
async def get_energetics_by_brand(brand_id: int = Path(..., description="ID бренда")):
    energetics = await EnergeticRepository.get_by_brand_id(brand_id)
    if not energetics:
        raise HTTPException(status_code=404, detail="No energetics found for the given brand ID")
    return energetics

@api_router.get("/api/users/{user_id}", response_model=UserModel)
async def get_user_by_id(user_id: int):
    return await UserRepository.get_user_by_id(user_id)

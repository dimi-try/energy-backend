from fastapi import APIRouter, Request, Depends, HTTPException, Path
from app.repository import EnergeticRepository, RatingRepository, BrandRepository, UserRepository
from app.schemas import EnergeticModel, RatingModel, BrandModel, UserModel
from app.auth import create_access_token, verify_token, validate
from typing import List
import time
import urllib.parse

# Создаем маршрутизатор для группировки API-эндпоинтов
api_router = APIRouter()

# Эндпоинт для проверки авторизации
@api_router.post("/auth/verify")
async def authorization_test(request: Request):
    # Извлекаем данные из запроса
    authorization_data = await request.json()
    # Парсим данные, чтобы достать hash и auth_date
    parsed_query = urllib.parse.parse_qs(authorization_data)
    hash_received = parsed_query.get('hash', [None])[0]
    auth_date = int(parsed_query.get('auth_date', [0])[0])

    # Проверка наличия хэша
    if not hash_received:
        raise HTTPException(status_code=400, detail="Hash not provided")

    # Валидация данных и проверка актуальности хэша
    if validate(hash_received, authorization_data):
        current_unix_time = int(time.time())
        timeout_seconds = 3600  # Таймаут на верификацию (1 час)
        if current_unix_time - auth_date > timeout_seconds:
            raise HTTPException(status_code=403, detail="Verification failed due to timeout")
        
        # Если верификация успешна, создаем токен доступа (JWT)
        access_token = create_access_token({"sub": "user_id"}, expires_delta=3600)
        return {"success": True, "message": "Verification successful", "access_token": access_token}
    else:
        raise HTTPException(status_code=403, detail="Verification failed")

# Защищенный эндпоинт, доступный только для авторизованных пользователей
@api_router.get("/auth/protected")
async def protected_endpoint(token: str = Depends(verify_token)):
    # Возвращаем сообщение и данные пользователя, извлеченные из токена
    return {"message": "Protected content", "user_data": token}

# Эндпоинт для получения списка всех энергетиков с рейтингами
@api_router.get("/api/energetics", response_model=List[EnergeticModel])
async def get_energetics():
    # Возвращаем данные через репозиторий энергетиков
    return await EnergeticRepository.get_all()

# Эндпоинт для добавления нового рейтинга для энергетика
@api_router.post("/api/ratings")
async def add_rating(rating: RatingModel, token: str = Depends(verify_token)):
    # Извлекаем user_id из токена
    user_id = token["sub"]
    # Добавляем новый рейтинг через репозиторий
    await RatingRepository.add_rating(user_id, rating)
    return {"success": True, "message": "Rating added"}

# Эндпоинт для обновления существующего рейтинга
@api_router.put("/api/ratings/{rating_id}")
async def update_rating(rating_id: int, rating: RatingModel, token: str = Depends(verify_token)):
    # Извлекаем user_id из токена
    user_id = token["sub"]
    # Обновляем рейтинг через репозиторий
    await RatingRepository.update_rating(rating_id, user_id, rating)
    return {"success": True, "message": "Rating updated"}

# Эндпоинт для удаления рейтинга
@api_router.delete("/api/ratings/{rating_id}")
async def delete_rating(rating_id: int, token: str = Depends(verify_token)):
    # Извлекаем user_id из токена
    user_id = token["sub"]
    # Удаляем рейтинг через репозиторий
    await RatingRepository.delete_rating(rating_id, user_id)
    return {"success": True, "message": "Rating deleted"}

# Эндпоинт для получения всех рейтингов для указанного энергетика по его id
@api_router.get("/api/ratings/{energy_id}", response_model=List[RatingModel])
async def get_ratings_by_energy(energy_id: int):
    # Получаем список рейтингов для энергетика через репозиторий
    return await RatingRepository.get_ratings_by_energy(energy_id)

# Эндпоинт для получения всех рейтингов, оставленных указанным пользователем
@api_router.get("/api/ratings/user/{user_id}", response_model=List[RatingModel])
async def get_ratings_by_user(user_id: int):
    # Получаем рейтинги пользователя через репозиторий
    return await RatingRepository.get_ratings_by_user(user_id)

# Эндпоинт для получения списка всех брендов с их рейтингами
@api_router.get("/api/brands", response_model=List[BrandModel])
async def get_brands():
    # Возвращаем данные через репозиторий брендов
    return await BrandRepository.get_all()

# Эндпоинт для получения всех энергетиков, принадлежащих конкретному бренду по его id
@api_router.get("/api/brand/{brand_id}/energetics", response_model=List[EnergeticModel])
async def get_energetics_by_brand(brand_id: int = Path(..., description="ID бренда")):
    # Получаем список энергетиков для бренда через репозиторий
    energetics = await EnergeticRepository.get_by_brand_id(brand_id)
    # Если энергетиков не найдено, возвращаем ошибку 404
    if not energetics:
        raise HTTPException(status_code=404, detail="No energetics found for the given brand ID")
    return energetics

# Эндпоинт для получения информации о пользователе по его id
@api_router.get("/api/users/{user_id}", response_model=UserModel)
async def get_user_by_id(user_id: int):
    # Возвращаем данные пользователя через репозиторий пользователей
    return await UserRepository.get_user_by_id(user_id)

from fastapi import APIRouter, Request, Depends, HTTPException
from app.repository import EnergeticRepository
from app.schemas import EnergeticModel
from app.auth import create_access_token, verify_token, validate
from typing import List
import time

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

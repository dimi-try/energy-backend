from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.security import create_access_token, validate_telegram_init_data
from app.services.users import get_user, create_user
from app.schemas.users import UserCreate
from app.db.database import get_db
import json

router = APIRouter()

@router.post("/verify", response_model=dict)
async def verify_telegram_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Эндпоинт для верификации Telegram initData и создания/получения пользователя.
    :param request: Запрос с initData в теле
    :param db: Сессия базы данных
    :return: JWT-токен и данные пользователя
    """
    # Получаем initData из тела запроса
    try:
        data = await request.json()
        init_data = data.get("init_data")
        if not init_data:
            raise HTTPException(status_code=400, detail="init_data не предоставлен")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Некорректный формат данных")

    # Валидируем initData и получаем данные пользователя
    user_data = validate_telegram_init_data(init_data)
    telegram_id = user_data.get("id")
    if not telegram_id:
        raise HTTPException(status_code=400, detail="user.id не найден в initData")

    # Проверяем, существует ли пользователь с таким telegram_id
    db_user = get_user(db, user_id=telegram_id)
    if not db_user:
        # Создаем нового пользователя
        user_create = UserCreate(
            username=user_data.get("username", f"user_{telegram_id}")
        )
        db_user = create_user(db, user=user_create, telegram_id=telegram_id)

    # Создаем JWT-токен с ролью
    access_token = create_access_token({"sub": str(telegram_id)}, db=db)

    return {
        "success": True,
        "message": "Верификация успешна",
        "access_token": access_token,
        "user_id": telegram_id
    }
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import json
import logging

from app.core.auth import get_user_role, create_access_token, validate_telegram_init_data
from app.core.config import TG_ADMIN_IDS

from app.db.database import get_db
from app.db.models import Role, UserRole

from app.schemas.users import UserCreate

from app.services.users import get_user, create_user

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    logger.info(f"Verifying user with telegram_id={telegram_id}")

    # Проверяем, существует ли пользователь
    db_user = get_user(db, user_id=telegram_id)
    if not db_user:
        # Создаем нового пользователя
        logger.info(f"User with telegram_id={telegram_id} not found, creating new user")
        user_create = UserCreate(
            username=user_data.get("username", f"user_{telegram_id}")
        )
        db_user = create_user(db, user=user_create, telegram_id=telegram_id)
    else:
        # Проверяем и обновляем роль для существующего пользователя
        logger.info(f"User with telegram_id={telegram_id} found, checking role")
        current_role = get_user_role(db, user_id=telegram_id)
        expected_role = "admin" if str(telegram_id) in TG_ADMIN_IDS else "user"
        if current_role != expected_role:
            logger.info(f"Updating role for telegram_id={telegram_id} to {expected_role}")
            # Удаляем старую роль, если она есть
            db.query(UserRole).filter(UserRole.user_id == telegram_id).delete()
            # Получаем роль из базы
            role = db.query(Role).filter(Role.name == expected_role).first()
            if not role:
                logger.error(f"Role {expected_role} not found in database")
                raise HTTPException(status_code=500, detail=f"Role {expected_role} not found in database")
            # Добавляем новую роль
            user_role = UserRole(user_id=telegram_id, role_id=role.id)
            db.add(user_role)
            db.commit()
            logger.info(f"Role {expected_role} assigned to telegram_id={telegram_id}")

    # Создаем JWT-токен с ролью
    access_token = create_access_token({"sub": str(telegram_id)}, db=db)

    return {
        "success": True,
        "message": "Верификация успешна",
        "access_token": access_token,
        "user_id": telegram_id
    }
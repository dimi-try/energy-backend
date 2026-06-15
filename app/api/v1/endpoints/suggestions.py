"""API endpoints для управления предложками энергетиков.

Предоставляет CRUD операции для предложок и позволяет администраторам
одобрять или отклонять их.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, verify_admin_token
from app.core.config import UPLOAD_DIR_SUGGESTION
from app.core.file_utils import upload_file

from app.db.database import get_db
from app.schemas.suggestions import (
    SuggestionCreate,
    SuggestionUpdate,
    SuggestionOut,
    SuggestionStatusOut,
)
from app.services.suggestions import (
    create_suggestion,
    get_user_suggestions,
    get_all_suggestions,
    update_suggestion,
    approve_suggestion,
    reject_suggestion,
    delete_suggestion,
)

# Создаём маршрутизатор для эндпоинтов предложок
router = APIRouter()

# Настройка OAuth2 для проверки JWT-токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/verify")

# =============== UPLOAD IMAGE ===============
@router.post("/upload-image/")
async def upload_suggestion_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Загрузка фото для предложки."""
    return await upload_file(file, UPLOAD_DIR_SUGGESTION)

# =============== CREATE ===============
@router.post("/", response_model=SuggestionOut, status_code=status.HTTP_201_CREATED)
def submit_suggestion(
    payload: SuggestionCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Создание новой предложки."""
    return create_suggestion(db, user["user_id"], payload)

# =============== READ ONE ===============
@router.get("/me", response_model=list[SuggestionOut])
def list_my_suggestions(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Получение списка предложок текущего пользователя."""
    return get_user_suggestions(db, user["user_id"])

# =============== READ ALL ===============
@router.get("/admin", response_model=list[SuggestionStatusOut])
def list_all_suggestions(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """Получение всех предложок (для админ-панели)."""
    verify_admin_token(token, db)
    return get_all_suggestions(db)

# =============== UPDATE ===============
@router.put("/{suggestion_id}", response_model=SuggestionOut)
def edit_suggestion(
    suggestion_id: int,
    payload: SuggestionUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Редактирование предложки."""
    suggestion = update_suggestion(db, user["user_id"], suggestion_id, payload)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return suggestion

# =============== DELETE ===============
@router.delete("/{suggestion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Удаление предложки пользователем."""
    result = delete_suggestion(db, user["user_id"], suggestion_id)
    if not result:
        raise HTTPException(status_code=404, detail="Suggestion not found or cannot be deleted")
    return None

# =============== ONLY ADMINS ===============

# =============== APPROVE ===============
@router.post("/{suggestion_id}/approve")
def admin_approve(
    suggestion_id: int,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """Одобрение предложки администратором."""
    verify_admin_token(token, db)
    result = approve_suggestion(db, suggestion_id)
    if not result:
        raise HTTPException(status_code=404, detail="Suggestion not found or cannot be approved")
    return {"success": True, "message": "Suggestion approved", "energy_id": result.id}

# =============== REJECT ===============
@router.post("/{suggestion_id}/reject", response_model=SuggestionOut)
def admin_reject(
    suggestion_id: int,
    comment: str | None = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """Отклонение предложки администратором."""
    verify_admin_token(token, db)
    result = reject_suggestion(db, suggestion_id, comment)
    if not result:
        raise HTTPException(status_code=404, detail="Suggestion not found or cannot be rejected")
    return result



import os
import uuid
from fastapi import HTTPException, status, UploadFile
from PIL import Image
import io
import pillow_heif
from app.core.config import UPLOAD_DIR_ENERGY, UPLOAD_DIR_REVIEW, UPLOAD_DIR_USER, ALLOWED_EXTENSIONS, MAX_FILE_SIZE

# Создание директорий
os.makedirs(UPLOAD_DIR_ENERGY, exist_ok=True)
os.makedirs(UPLOAD_DIR_REVIEW, exist_ok=True)
os.makedirs(UPLOAD_DIR_USER, exist_ok=True)

def validate_file(file: UploadFile):
    """Валидация загружаемого файла: проверка формата и размера."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый формат файла. Разрешены: JPG, JPEG, PNG, HEIC, HEIF"
        )
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл слишком большой. Максимальный размер: 5 МБ"
        )
    try:
        img = Image.open(file.file)
        img.verify()  # Проверяем, что это валидное изображение
        file.file.seek(0)  # Сбрасываем указатель файла
        return ext
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невалидный файл изображения"
        )

async def upload_file(file: UploadFile, upload_dir: str):
    """Загрузка файла на сервер с конвертацией HEIC, HEIF, JPG, JPEG в PNG."""
    ext = validate_file(file)
    file_name = f"{uuid.uuid4()}.png"  # Всегда сохраняем как PNG
    file_path = os.path.join(upload_dir, file_name)
    
    try:
        img = Image.open(file.file)
        output = io.BytesIO()
        img.save(output, format="PNG")  # Конвертируем в PNG
        content = output.getvalue()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Формируем полный URL
        relative_path = os.path.join(upload_dir, file_name).replace("\\", "/")
        full_url = f"{relative_path}"
        return {"image_url": full_url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при загрузке файла: {str(e)}"
        )
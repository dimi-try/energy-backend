import os
import uuid
from fastapi import HTTPException, status, UploadFile
from PIL import Image
import io
from config import UPLOAD_DIR_ENERGY, UPLOAD_DIR_REVIEW, UPLOAD_DIR_USER, ALLOWED_EXTENSIONS, MAX_FILE_SIZE

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
            detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // (1024 * 1024)} МБ"
        )
    try:
        img = Image.open(file.file)
        img.verify()  # Проверяем, что это валидное изображение
        file.file.seek(0)  # Сбрасываем указатель файла
        return ext
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невалидный файл изображения: {str(e)}"
        )

async def upload_file(file: UploadFile, upload_dir: str):
    """Загрузка файла на сервер без конвертации с удалением метаданных."""
    ext = validate_file(file)
    file_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(upload_dir, file_name)

    try:
        img = Image.open(file.file)
        output = io.BytesIO()
        
        if ext in [".jpg", ".jpeg"]:
            # Сохраняем JPEG без метаданных
            img.save(output, format="JPEG", quality=95, exif=b"")
        elif ext in [".heic", ".heif"]:
            # Сохраняем HEIC/HEIF без метаданных
            img.save(output, format="HEIF")
        else:
            # Сохраняем PNG без метаданных
            img.save(output, format="PNG")

        content = output.getvalue()
        
        # Сохраняем файл
        with open(file_path, "wb") as f:
            f.write(content)
        return {"image_url": file_path}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при загрузке файла: {str(e)}"
        )
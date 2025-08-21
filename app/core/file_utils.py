import os
import uuid
from fastapi import HTTPException, status, UploadFile
from PIL import Image
import io
from dotenv import load_dotenv

load_dotenv()

# Константы из .env
UPLOAD_DIR_ENERGY = os.getenv("UPLOAD_DIR_ENERGY", "uploads/energy/")
UPLOAD_DIR_REVIEW = os.getenv("UPLOAD_DIR_REVIEW", "uploads/reviews/")
ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", ".jpg,.jpeg,.png,.heic").split(","))
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 5 * 1024 * 1024))  # 5 MB

# Создание директорий
os.makedirs(UPLOAD_DIR_ENERGY, exist_ok=True)
os.makedirs(UPLOAD_DIR_REVIEW, exist_ok=True)

def validate_file(file: UploadFile):
    """Валидация загружаемого файла: проверка формата и размера."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый формат файла. Разрешены: JPG, JPEG, PNG, HEIC"
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

async def upload_file(file: UploadFile, upload_dir: str, convert_heic: bool = True):
    """Загрузка файла на сервер с конвертацией HEIC в PNG при необходимости."""
    ext = validate_file(file)
    file_name = f"{uuid.uuid4()}{'.png' if ext == '.heic' and convert_heic else ext}"
    file_path = os.path.join(upload_dir, file_name)
    
    try:
        img = Image.open(file.file)
        if ext == ".heic" and convert_heic:
            output = io.BytesIO()
            img.save(output, format="PNG")
            content = output.getvalue()
        else:
            content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        return {"image_url": file_path}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при загрузке файла: {str(e)}"
        )
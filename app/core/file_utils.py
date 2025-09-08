import os
import uuid
import logging
from fastapi import HTTPException, status, UploadFile
from PIL import Image
import io
import pillow_heif
from app.core.config import UPLOAD_DIR_ENERGY, UPLOAD_DIR_REVIEW, UPLOAD_DIR_USER, ALLOWED_EXTENSIONS, MAX_FILE_SIZE

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Регистрация HEIF/HEIC в Pillow
pillow_heif.register_heif_opener()

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
        file.file.seek(0)  # Сбрасываем указатель файла
        return ext
    except Exception as e:
        logger.error(f"Ошибка валидации файла {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Невалидный файл изображения: {str(e)}"
        )

async def upload_file(file: UploadFile, upload_dir: str):
    """Загрузка файла на сервер с конвертацией в PNG, сохранением исходного разрешения и удалением метаданных."""
    ext = validate_file(file)
    file_name = f"{uuid.uuid4()}.png"  # Всегда сохраняем как PNG
    file_path = os.path.join(upload_dir, file_name)
    
    try:
        img = Image.open(file.file)
        logger.info(f"Формат изображения: {img.format}, режим: {img.mode}, размер: {img.size}")
        
        # Конвертируем в RGB для удаления метаданных и обеспечения совместимости
        img = img.convert("RGB")
        
        # Очищаем метаданные (на всякий случай)
        img.info.clear()
        
        # Сохраняем в PNG без сжатия, чтобы сохранить качество
        output = io.BytesIO()
        img.save(output, format="PNG", quality=100, compress_level=0)  # Без сжатия
        content = output.getvalue()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Формируем полный URL
        relative_path = os.path.join(upload_dir, file_name).replace("\\", "/")
        full_url = f"{relative_path}"
        return {"image_url": full_url}
    except Exception as e:
        logger.error(f"Ошибка при загрузке файла {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при загрузке файла: {str(e)}"
        )
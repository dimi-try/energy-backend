import os
from dotenv import load_dotenv

load_dotenv()

# =============== База данных ===============
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# =============== Шифрование ===============
BACKEND_SECRET_KEY = os.getenv("BACKEND_SECRET_KEY")
BACKEND_ALGORITHM = os.getenv("BACKEND_ALGORITHM")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# =============== Админ-панель ===============
TG_ADMIN_IDS = os.getenv("TG_ADMIN_IDS", "").split(",")

# =============== Разрешенные для CORS адреса ===============
FRONTEND_URL = os.getenv("FRONTEND_URL")

# =============== Настройки загрузки файлов ===============
UPLOAD_DIR_ENERGY = os.getenv("UPLOAD_DIR_ENERGY", "uploads/energy/")
UPLOAD_DIR_REVIEW = os.getenv("UPLOAD_DIR_REVIEW", "uploads/reviews/")
ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", ".jpg,.jpeg,.png,.heic").split(","))
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 5 * 1024 * 1024))  # 5 MB
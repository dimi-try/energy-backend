import os
import csv
import random #для рандома описания и разных выборов
import string  #для генерации описания
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
from app import models  # Импорт моделей SQLAlchemy
from decimal import Decimal, ROUND_HALF_UP #для округления

# Конфигурация
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
alembic_cfg = Config("alembic.ini")

def random_description(length=10):  
    """Рандомное описание энергетика"""
    words = ["".join(random.choices(string.ascii_lowercase, k=random.randint(3, 10))) for _ in range(length)]  
    return " ".join(words).capitalize() + "."  

def generate_rating_value() -> float:
    # Генерируем случайное число от 0 до 10 с плавающей точкой
    random_value = random.uniform(0, 10)
    # Округляем до 4 знаков после запятой
    rounded_value = Decimal(random_value).quantize(Decimal('0.0000'), rounding=ROUND_HALF_UP)
    return float(rounded_value)

def reset_database():
    """Полная очистка базы данных"""
    try:
        with engine.begin() as conn:
            # Удаление всей структуры БД
            conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
            conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
        print("🔥 База данных полностью сброшена")
    except Exception as e:
        print(f"❌ Ошибка сброса: {e}")
        raise

def clean_and_apply_migrations():
    """Удаляет старые миграции, создает новые и применяет их"""
    try:
        # Удаляем старые миграции
        alembic_versions_dir = "alembic/versions"
        if os.path.exists(alembic_versions_dir):
            for f in os.listdir(alembic_versions_dir):
                file_path = os.path.join(alembic_versions_dir, f)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        print("🧹 Старые миграции удалены")

        # Создание новой миграции
        command.revision(alembic_cfg, autogenerate=True, message="Initial")
        print("🔄 Миграция успешно сгенерирована")

        # Применение миграций
        command.upgrade(alembic_cfg, "head")
        print("🔄 Миграции успешно применены")
    except Exception as e:
        print(f"❌ Ошибка с миграциями: {e}")
        raise

def seed_data():
    """Заполнение тестовыми данными"""
    db = SessionLocal()
    
    try:
        # 3.1 Пользователи
        users = [
            models.User(
                username="test_user_1",
                email="user1@example.com",
                password="password1",
                is_premium=False,
                created_at=datetime.now()
            ),
            models.User(
                username="test_user_2",
                email="user2@example.com",
                password="password2",
                is_premium=True,
                created_at=datetime.now()
            )
        ]
        db.add_all(users)
        db.commit()

        # 3.2 Категории
        categories = [
            models.Category(name="Алкогольный энергетик"),
            models.Category(name="Обычный энергетик"),
            models.Category(name="Энергетик без сахара"),
            models.Category(name="Чай/Витамины")
        ]
        db.add_all(categories)
        db.commit()

        # 3.3 Критерии
        criteria = [
            models.Criteria(name="Вкус"),
            models.Criteria(name="Цена"),
            models.Criteria(name="Химоза")
        ]
        db.add_all(criteria)
        db.commit()

        # 3.4 Бренды и энергетики
        brands = {}
        with open("test_data.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Создаем бренд, если его нет
                brand_name = row["model"].strip()
                if brand_name not in brands:
                    brand = models.Brand(name=brand_name)
                    db.add(brand)
                    db.commit()
                    db.refresh(brand)
                    brands[brand_name] = brand.id

                # Создаем энергетик
                energy = models.Energy(
                    name=row["name"].strip(),
                    brand_id=brands[brand_name],
                    category_id=random.choice(categories).id,  # Случайная категория
                    description=random_description(), # Создает рандомное описание из набора букв
                    image_url=row.get("image_url", ""),
                    ingredients=row.get("ingredients", "")
                )
                db.add(energy)
                db.commit()

                # Создаем отзыв
                review = models.Review(
                    user_id=random.choice(users).id, #рандомно выбираем юзера который это написал вместо users[0].id
                    energy_id=energy.id,
                    review_text=row["description"],
                    created_at=datetime.strptime(row["date"], "%Y-%m-%d")
                )
                db.add(review)
                db.commit()

                # Создаем оценки
                ratings = [
                    models.Rating(
                        review_id=review.id,
                        criteria_id=criteria[0].id,
                        rating_value=float(row["rating"])
                    ),
                    models.Rating(
                        review_id=review.id,
                        criteria_id=criteria[1].id,
                        rating_value=generate_rating_value()  # Генерация с округлением
                    ),
                    models.Rating(
                        review_id=review.id,
                        criteria_id=criteria[2].id,
                        rating_value=generate_rating_value()  # Генерация с округлением
                    )
                ]
                db.add_all(ratings)
                db.commit()

        print("✅ Данные успешно загружены!")

    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    reset_database()  # Сбрасываем базу данных
    clean_and_apply_migrations()  # Чистим старые миграции и применяем новые
    seed_data()  # Загружаем данные

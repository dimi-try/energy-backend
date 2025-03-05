import csv
from sqlalchemy.orm import Session
from app import models
from app.database import SessionLocal
from datetime import datetime

# Путь к CSV файлу
CSV_FILE = "test_data.csv"  # Обновленный путь к файлу

def seed_data(db: Session):
    # Очищаем старые данные из таблиц
    db.query(models.Rating).delete()
    db.query(models.Energy).delete()
    db.query(models.Brand).delete()
    db.query(models.User).delete()
    db.query(models.Category).delete()  # Если категория будет в проекте
    db.query(models.Criteria).delete()  # Удаляем старые критерии
    db.commit()

    # Создание пользователей
    user1 = models.User(username="test_user_1", email="user1@mail.com", password="password1", is_premium=False)
    user2 = models.User(username="test_user_2", email="user2@mail.com", password="password2", is_premium=True)
    db.add_all([user1, user2])
    db.commit()

    # Пример создания категорий
    category1 = models.Category(name="Предтреник")
    category2 = models.Category(name="Энергетический напиток")
    db.add_all([category1, category2])
    db.commit()

    # Создание критериев (например, Вкус, Цена, Энергетический эффект)
    criteria1 = models.Criteria(name="Вкус")
    criteria2 = models.Criteria(name="Цена")
    criteria3 = models.Criteria(name="Энергетический эффект")
    db.add_all([criteria1, criteria2, criteria3])
    db.commit()

    # Чтение данных из CSV
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # 1. Получаем или создаем бренд
            brand_name = row["model"].strip()
            brand = db.query(models.Brand).filter(models.Brand.name == brand_name).first()
            if not brand:
                brand = models.Brand(name=brand_name)
                db.add(brand)
                db.commit()
                db.refresh(brand)

            # 2. Создаем энергетик
            energy = models.Energy(
                id=row["id"],  # Используем ID из CSV файла
                name=row["name"].strip(),
                brand_id=brand.id,  # Связь с брендом
                description=row["description"].strip(),
                category_id=category1.id,  # Пример категории, можно модифицировать
            )
            db.add(energy)
            db.commit()

            # 3. Добавляем рейтинг и отзыв
            # Для простоты используем user1 и user2 для добавления рейтингов
            rating1 = models.Rating(
                user_id=user1.id,
                energy_id=energy.id,
                criteria_id=criteria1.id,  # Используем ID критерия для "Вкус"
                rating=row["rating"],
                review=row["description"].strip(),  # Используем описание как текст отзыва
                created_at=datetime.strptime(row["date"], "%Y-%m-%d")  # Преобразуем строку в дату
            )
            db.add(rating1)

            rating2 = models.Rating(
                user_id=user2.id,
                energy_id=energy.id,
                criteria_id=criteria2.id,  # Используем ID критерия для "Цена"
                rating=row["rating"],  # Можем использовать тот же рейтинг или изменить
                review=row["description"].strip(),  # Тот же отзыв
                created_at=datetime.strptime(row["date"], "%Y-%m-%d")  # Используем ту же дату
            )
            db.add(rating2)
            db.commit()

    print("Данные успешно добавлены!")

# Подключение к БД и запуск seed-функции
if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()

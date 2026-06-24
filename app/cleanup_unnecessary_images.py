"""
Скрипт для очистки ненужных фотографий, которые не используются в БД.

Сканирует директории загрузок и удаляет файлы, на которые нет ссылок
в таблицах: energetics, reviews, suggestions, users.

Безопасность:
- Использует ORM SQLAlchemy (параметризованные запросы) - защита от SQL-инъекций
- Только чтение из БД, никаких модификаций
- Работает только с указанными директориями загрузок
- Режим dry-run по умолчанию (требуется --execute для удаления)
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Импортируем конфигурацию
from app.core.config import (
    DATABASE_URL,
    UPLOAD_DIR_ENERGY,
    UPLOAD_DIR_REVIEW,
    UPLOAD_DIR_SUGGESTION,
    UPLOAD_DIR_USER,
)

# Импортируем модели для безопасного ORM-доступа
from app.db.models import Energy, Review, Suggestion, User

# Создаём движок и сессию БД
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_used_images_from_db() -> set:
    """
    Получает все пути к изображениям, которые используются в БД.
    Использует ORM SQLAlchemy для безопасного доступа к данным.
    """
    used_images = set()
    
    with SessionLocal() as db:
        # Получаем изображения из таблицы energetics
        for energy in db.query(Energy.image_url).filter(Energy.image_url.isnot(None)).all():
            if energy.image_url:
                used_images.add(energy.image_url)
        
        # Получаем изображения из таблицы reviews
        for review in db.query(Review.image_url).filter(Review.image_url.isnot(None)).all():
            if review.image_url:
                used_images.add(review.image_url)
        
        # Получаем изображения из таблицы suggestions
        for suggestion in db.query(Suggestion.image_url).filter(Suggestion.image_url.isnot(None)).all():
            if suggestion.image_url:
                used_images.add(suggestion.image_url)
        
        # Получаем изображения из таблицы users
        for user in db.query(User.image_url).filter(User.image_url.isnot(None)).all():
            if user.image_url:
                used_images.add(user.image_url)
    
    return used_images


def get_files_in_directory(directory: str) -> set:
    """Получает все файлы в директории (рекурсивно)."""
    files = set()
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"Директория {directory} не существует, пропускаем...")
        return files
    
    for file_path in dir_path.rglob("*"):
        if file_path.is_file():
            files.add(str(file_path))
    
    return files


def normalize_path(path: str) -> str:
    """Нормализует путь для сравнения (убирает ./ и нормализует слеши)."""
    return str(Path(path))


def find_orphan_images(upload_dirs: list, used_images: set) -> list:
    """Находит файлы, которые есть на диске, но нет в БД."""
    all_files = set()
    
    # Собираем все файлы из всех директорий загрузок
    for upload_dir in upload_dirs:
        files = get_files_in_directory(upload_dir)
        all_files.update(files)
    
    # Нормализуем пути в used_images для сравнения
    normalized_used = {normalize_path(img) for img in used_images}
    
    # Находим "сирот" - файлы, которых нет в БД
    orphan_files = []
    for file_path in all_files:
        normalized_path = normalize_path(file_path)
        if normalized_path not in normalized_used:
            orphan_files.append(file_path)
    
    return orphan_files


def delete_orphan_images(orphan_files: list, dry_run: bool = True) -> None:
    """Удаляет или выводит список "сирот" файлов."""
    if not orphan_files:
        print("Ненужных файлов не найдено!")
        return
    
    action = "Будут удалены" if dry_run else "Удаляем"
    print(f"\n{action} {len(orphan_files)} файлов:")
    print("-" * 60)
    
    total_size = 0
    for file_path in orphan_files:
        file_size = os.path.getsize(file_path)
        total_size += file_size
        size_mb = file_size / (1024 * 1024)
        print(f"  {file_path} ({size_mb:.2f} MB)")
        
        if not dry_run:
            try:
                os.remove(file_path)
                print(f"    -> Удалено")
            except Exception as e:
                print(f"    -> Ошибка удаления: {e}")
    
    print("-" * 60)
    total_size_mb = total_size / (1024 * 1024)
    print(f"Общий размер: {total_size_mb:.2f} MB")
    
    # Удаляем пустые директории
    if not dry_run:
        cleanup_empty_dirs()


def cleanup_empty_dirs() -> None:
    """Удаляет пустые директории после очистки файлов."""
    upload_dirs = [
        UPLOAD_DIR_ENERGY,
        UPLOAD_DIR_REVIEW,
        UPLOAD_DIR_SUGGESTION,
        UPLOAD_DIR_USER,
    ]
    
    for upload_dir in upload_dirs:
        dir_path = Path(upload_dir)
        if dir_path.exists():
            for root, dirs, files in os.walk(str(dir_path), topdown=False):
                for dir_name in dirs:
                    full_path = Path(root) / dir_name
                    try:
                        if not any(full_path.iterdir()):
                            full_path.rmdir()
                            print(f"Удалена пустая директория: {full_path}")
                    except Exception:
                        pass


def main() -> None:
    """Основная функция."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Очистка ненужных фотографий, не используемых в БД"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Фактически удалить файлы (по умолчанию только показать)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Показать все используемые изображения"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Скрипт очистки ненужных фотографий")
    print("=" * 60)
    
    # Получаем используемые изображения из БД
    print("\nПолучаем данные из БД...")
    used_images = get_used_images_from_db()
    print(f"Найдено {len(used_images)} изображений в БД")
    
    if args.verbose:
        print("\nИспользуемые изображения:")
        for img in sorted(used_images):
            print(f"  {img}")
    
    # Директории для сканирования
    upload_dirs = [
        UPLOAD_DIR_ENERGY,
        UPLOAD_DIR_REVIEW,
        UPLOAD_DIR_SUGGESTION,
        UPLOAD_DIR_USER,
    ]
    
    # Находим "сирот"
    print("\nСканируем директории...")
    orphan_files = find_orphan_images(upload_dirs, used_images)
    
    # Удаляем или показываем
    dry_run = not args.execute
    if dry_run and orphan_files:
        print("\n[DRY RUN] Для фактического удаления запустите с флагом --execute")
    
    delete_orphan_images(orphan_files, dry_run=dry_run)
    
    print("\nГотово!")


if __name__ == "__main__":
    main()
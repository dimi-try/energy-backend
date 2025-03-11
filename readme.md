# Backend приложения "Топ энергетиков"

## 🚀 О проекте

Этот репозиторий содержит backend-приложение "Топ энергетиков", разработанное на **FastAPI** с использованием **PostgreSQL** и **Alembic**.

## 💻 Технологии

[![Технологии](https://skillicons.dev/icons?i=fastapi,py,postgres)](https://skillicons.dev)

## 📂 Структура проекта

```sh
ergy-backend/
│
├── .env                # Переменные окружения
├── .gitignore          # Исключаемые файлы
├── README.md           # Документация
├── alembic/
│   ├── env.py          # Конфигурация Alembic
│   ├── versions/       # Папка с миграциями
│
├── alembic.ini         # Файл конфигурации Alembic
│
├── app/
│   ├── __init__.py     # Инициализация модуля Python
│   ├── api.py          # Роуты API
│   ├── crud.py         # CRUD операции
│   ├── database.py     # Подключение к базе данных
│   ├── main.py         # Точка входа FastAPI
│   ├── models.py       # SQLAlchemy модели
│   ├── schemas.py      # Pydantic схемы
│
├── docker-compose.yml  # Конфигурация Docker с PostgreSQL
├── load_test_data.py   # Скрипт загрузки тестовых данных (включает миграции)
├── requirements.txt    # Зависимости проекта
├── test_data.csv       # Тестовые данные
├── venv/               # Виртуальное окружение
```

---

## ⚡ Установка и запуск

### 1️⃣ Подготовка окружения

#### Установка зависимостей
```bash
pip install -r requirements.txt
```

#### Создание и активация виртуального окружения
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
```

### 2️⃣ Настройка и запуск Backend

#### Автоматическая подготовка базы данных и миграций

Просто выполните следующую команду — она подготовит базу, выполнит миграции и загрузит тестовые данные:
```bash
python load_test_data.py
```

#### Запуск сервера FastAPI
```bash
uvicorn app.main:app --reload
```

---

## 📌 Работа с Alembic

Alembic используется для управления миграциями базы данных.

### Основные команды:

- Создание новой миграции:
  ```bash
  alembic revision --autogenerate -m "Описание изменений"
  ```
- Применение миграций:
  ```bash
  alembic upgrade head
  ```
- Откат миграции:
  ```bash
  alembic downgrade -1
  ```

---

## 🛠 Полезные команды

### Просмотр установленных зависимостей
```bash
pip list
```

### Сохранение зависимостей
```bash
pip freeze > requirements.txt
```

### Удаление всех зависимостей
```bash
pip uninstall -y -r requirements.txt
```

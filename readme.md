# 🚀 Backend-приложение "Топ энергетиков"

Добро пожаловать в **"Топ энергетиков"** — backend-приложение на **FastAPI**, созданное для оценки и выбора лучших энергетических напитков. Здесь пользователи могут оставлять отзывы, выставлять оценки и анализировать статистику популярных напитков. Проект использует **PostgreSQL** и **Alembic** для надежного хранения и управления данными. 🚀

## 🛠 Используемые технологии

[![FastAPI](https://skillicons.dev/icons?i=py,fastapi,postgres)](https://skillicons.dev)

## 📂 Структура проекта

```sh
energy-backend/
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

#### 📌 Установка зависимостей
```bash
pip install -r requirements.txt
```

#### 🔧 Создание и активация виртуального окружения
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
```

#### 📋 Настройка .env
Скопируйте `.env.sample`, переименуйте в `.env` и добавьте свои данные.

### 2️⃣ Запуск Backend

#### 🔍 Автоматическая подготовка базы данных и миграций
Выполните команду для инициализации базы данных, применения миграций и загрузки тестовых данных:
```bash
python load_test_data.py
```

#### 🚀 Запуск сервера FastAPI
```bash
uvicorn app.main:app --reload
```

---

## 🔄 Работа с Alembic

Alembic используется для управления миграциями базы данных.

### Основные команды:

- 📌 **Создание новой миграции:**
  ```bash
  alembic revision --autogenerate -m "Описание изменений"
  ```
- 📌 **Применение миграций:**
  ```bash
  alembic upgrade head
  ```
- 📌 **Откат миграции:**
  ```bash
  alembic downgrade -1
  ```

---

## 🛠 Полезные команды

📌 **Просмотр установленных зависимостей**
```bash
pip list
```

💾 **Сохранение зависимостей**
```bash
pip freeze > requirements.txt
```

🗑 **Удаление всех зависимостей**
```bash
pip uninstall -y -r requirements.txt
```

---

💡 **Если у вас есть вопросы или предложения по улучшению проекта, создайте issue!** 🚀

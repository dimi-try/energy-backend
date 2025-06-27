# 🚀 Backend-приложение "Топ энергетиков"

Добро пожаловать в **"Топ энергетиков"** — backend-приложение на **FastAPI**, созданное для оценки и выбора лучших энергетических напитков. Здесь пользователи могут оставлять отзывы, выставлять оценки и анализировать статистику популярных напитков. Проект использует **PostgreSQL** и **Alembic** для надежного хранения и управления данными. 🚀

## 🛠 Используемые технологии

[![Technologies](https://skillicons.dev/icons?i=py,fastapi,postgres)](https://skillicons.dev)

## 📂 Структура проекта

```sh
energy-backend/
│
├── .github/
│   └── workflows/
│       └── docker-deploy.yml   # CI/CD: деплой Docker-контейнера
│
├── alembic/
│   ├── versions/               # Папка с миграциями
│   └── env.py                  # Конфигурация Alembic
│
├── app/        
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py # Инициализация модуля Python
│   │   │   │   └── ... .py     # Роуты API (эндпоинты)
│   │   │   ├── __init__.py     # Инициализация модуля Python
│   │   │   └── router.py       # Объединяет маршруты версии v1
│   │   └── __init__.py         # Инициализация модуля Python
│   ├── core/           
│   │   ├── __init__.py         # Инициализация модуля Python
│   │   ├── config.py           # Конфигурация приложения
│   │   └── security.py         # Логика авторизации (JWT, валидация)
│   ├── db/
│   │   ├── models/
│   │   │   ├── __init__.py     # Инициализация модуля Python
│   │   │   ├── base.py         # Базовый класс для моделей
│   │   │   └── ... .py         # SQLAlchemy модели
│   │   ├── __init__.py         # Инициализация модуля Python
│   │   └── database.py         # Настройка подключения к БД
│   ├── schemas/        
│   │   ├── __init__.py         # Инициализация модуля Python
│   │   └── ... .py             # Pydantic схемы
│   ├── services/       
│   │   ├── __init__.py         # Инициализация модуля Python
│   │   └── ... .py             # CRUD операции (Бизнес логика)
│   ├── test/
│   │   ├── __init__.py         # Инициализация модуля Python
│   │   └── load_test_data.py   # Скрипт загрузки тестовых данных (включает миграции)
│   ├── __init__.py             # Инициализация модуля Python
│   └── main.py                 # Точка входа FastAPI
│
├── .dockerignore               # Исключения для сборки контейнера
├── .env.sample                 # Пример файла с переменными окружения
├── .gitignore                  # Исключаемые файлы
├── alembic.ini                 # Файл конфигурации Alembic
├── docker-compose-server.yml   # Конфигурация Docker с PostgreSQL для сервера
├── docker-compose.yml          # Конфигурация Docker
├── Dockerfile                  # Docker конфигурация
├── README.md                   # Документация
├── requirements.txt            # Зависимости проекта
└── test_data.csv               # Тестовые данные
```

---

## ⚡ Установка и запуск

### 1️⃣ Подготовка окружения

#### 📋 Настройка .env
Скопируйте `.env.sample`, переименуйте в `.env` и добавьте свои данные.

#### 🔧 Создание и активация виртуального окружения

Создание 
```bash
python -m venv venv
```
Активация
```bash
venv\Scripts\activate  # Windows
```
```bash
source venv/bin/activate  # Linux/macOS
```

#### 📌 Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2️⃣ Запуск Backend

#### 🔍 Автоматическая подготовка базы данных и миграций
Выполните команду для инициализации базы данных, применения миграций и загрузки тестовых данных:
```bash
python -m app.test.load_test_data
```

#### 🚀 Запуск сервера FastAPI
```bash
uvicorn app.main:app --reload
```

API будет доступно по адресу:  
📍 `http://localhost:8000`

---

## 🌍 Деплой

Доступны два способа:

### Вариант 1: Docker Compose вручную

1.  Проверьте `docker-compose.yml`
    
2.  Выполните сборку и пуш:
    

```sh
docker compose build
```
```sh
docker compose up -d
```
```sh
docker push <your-dockerhub>
```

### Вариант 2: Автоматически через GitHub Actions

1.  В файле `.github/workflows/docker-deploy.yml` уже всё готово
    
2.  При пуше в `main` ветку произойдёт автоматическая сборка и публикация образа в DockerHub
    

На прод-сервере можете использовать `docker-compose-server.yml` из [репозитория backend](https://github.com/dimi-try/energy-backend). Скопируйте `.env.example`, переименуйте в `.env` и добавьте свои данные.

#### 🔍 Автоматическая подготовка базы данных и миграций
Если вам нужно поменять тестовые данные на сервере, то вы можете сделать следующее:

Войти в контейнер
```
docker exec -it ens-backend-1 /bin/sh
```

Если папки versions нет, создать ее:
```
mkdir -p /app/alembic/versions
```

Запустить скрипт загрузки тестовых данных
```
python load_test_data.py
```

---

## 📡 Интеграция с frontend

Backend работает в связке с frontend-приложением [energy-frontend](https://github.com/dimi-try/energy-frontend).  
Убедитесь, что:

-   `REACT_APP_BACKEND_URL` указывает на корректный хост backend-а,
    
-   разрешено CORS-соединение с фронта.
    

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

🧹 **Удаление виртуального окружения venv**
```powershell
Get-ChildItem -Path . -Recurse -Directory -Filter "venv" | Remove-Item -Recurse -Force #windows
```

🧹 **Удаление кеша pycache**
```powershell
Get-ChildItem -Recurse -Directory -Include "__pycache__", ".mypy_cache", ".pytest_cache" | Remove-Item -Recurse -Force #windows
Get-ChildItem -Recurse -Include *.pyc | Remove-Item -Force #windows
```

---

💡 **Если у вас есть вопросы или предложения по улучшению проекта, создайте issue!** 🚀

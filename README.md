# 🚀 Backend-приложение "Топ энергетиков"

Добро пожаловать в **"Топ энергетиков"** — backend-приложение на **FastAPI**, созданное для оценки и выбора лучших энергетических напитков. Здесь пользователи могут оставлять отзывы, выставлять оценки и анализировать статистику популярных напитков. Проект использует **PostgreSQL** и **Alembic** для надежного хранения и управления данными. 🚀

## 🛠 Используемые технологии

[![FastAPI](https://skillicons.dev/icons?i=py,fastapi,postgres)](https://skillicons.dev)

## 📂 Структура проекта

```sh
energy-backend/
│
├── .github/
│   └── workflows/
│       └── docker-deploy.yml         # CI/CD: деплой Docker-контейнера
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

#### 📋 Настройка .env
Скопируйте `.env.sample`, переименуйте в `.env` и добавьте свои данные.

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
    

На прод-сервере можете использовать `docker-compose-server.yml` из [репозитория backend](https://github.com/dimi-try/energy-backend). Не забудьте создать свой `.env` для этого файла.

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

---

💡 **Если у вас есть вопросы или предложения по улучшению проекта, создайте issue!** 🚀

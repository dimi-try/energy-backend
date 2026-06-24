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
│   │   └── loader_data.py      # Скрипт загрузки тестовых данных (включает миграции)
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
└── data.csv                    # Тестовые данные
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
python -m app.test.loader_data
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
docker exec -it energy-backend-1 /bin/sh
```

Установить nano (по желанию, если вам удобнее пользоваться nano):
```
apk add --no-cache nano   # если контейнер на Alpine
```
или
```
apt-get update && apt-get install -y nano   # если Debian/Ubuntu
```

Заменить тестовые данные на свои
```
nano data.csv
```

Если папки versions нет, создать ее:
```
mkdir -p /app/alembic/versions
```

Запустить скрипт загрузки тестовых данных
```
python -m app.test.loader_data
```

#### 🔍 Удаление ненужных или дублирующихся фотографий, неиспользуемых в БД

Войти в контейнер
```
docker exec -it energy-backend-1 /bin/sh
```

Показать что будет удалено (безопасно)
```
python -m app.cleanup_unnecessary_images
```

Показать все используемые изображения
```
python -m app.cleanup_unnecessary_images --verbose
```

Фактически удалить ненужные файлы
```
python -m app.cleanup_unnecessary_images --execute
```

---
## 🖼 Резервное копирование изображений

### 📤 Выгрузка изображений из контейнера

1️⃣ Проверить, существуют ли папки с изображениями уже на сервере
```
find / -type d -name "image-backup" 2>/dev/null
```

```
find / -type d -name "image-backup-tar" 2>/dev/null
```

2️⃣ Скопировать папку uploads из контейнера на сервер
```
docker cp energy-backend-1:/app/uploads /image-backup/
```

3️⃣ Создать архив с изображениями
```
mkdir -p /image-backup-tar
```

```
tar -czf /image-backup-tar/uploads-backup.tar.gz -C /image-backup/ .
```

4️⃣ Скопировать архив с сервера на локальную машину

👉 Windows (PowerShell):
```
scp -r user@server:/image-backup-tar/ C:\Users\USER\Downloads\
```

👉 Linux/macOS:
```
scp -r user@server:/image-backup-tar/ ~/Downloads/
```

5️⃣ Очистить временную папку на сервере
```
rm -rf /image-backup/
```

```
rm -rf /image-backup-tar/
```

6️⃣ Проверить, остались ли папки на сервере
```
find / -type d -name "image-backup" 2>/dev/null
```

```
find / -type d -name "image-backup-tar" 2>/dev/null
```
---

### 📥 Загрузка изображений обратно в контейнер

1️⃣ Проверить, существуют ли папки с изображениями уже на сервере
```
find / -type d -name "image-backup" 2>/dev/null
```

```
find / -type d -name "image-backup-tar" 2>/dev/null
```

2️⃣ Создать папки с изображениями
```
mkdir -p /image-backup
```

```
mkdir -p /image-backup-tar
```

3️⃣ Скопировать изображения с локалки на сервер

👉 Windows (PowerShell):
```
scp C:\Users\USER\Downloads\image-backup-tar\uploads-backup.tar.gz user@server:/image-backup-tar/
```

👉 Linux/macOS:
```
scp ~/Downloads/uploads-backup.tar.gz user@server:/image-backup-tar/
```

4️⃣ Распаковать архив на сервере
```
tar -xzf /image-backup-tar/uploads-backup.tar.gz -C /image-backup/
```

5️⃣ Перенести изображения с сервера в контейнер
```
docker cp /image-backup/. energy-backend-1:/app/uploads
```

6️⃣ Очистить временные папки на сервере
```
rm -rf /image-backup/
```

```
rm -rf /image-backup-tar/
```

7️⃣ Проверить, остались ли папки на сервере
```
find / -type d -name "image-backup" 2>/dev/null
```

```
find / -type d -name "image-backup-tar" 2>/dev/null
```

---
## 🗄 Резервное копирование базы данных

### 📤 Создание резервной копии

1️⃣ Проверить, существует ли бэкап уже на сервере
```
find / -type f -name "*energy_drink*" 2>/dev/null
```

2️⃣ Заходим в контейнер с PostgreSQL:
```
docker exec -it energy-postgres-1 bash
```

3️⃣ Делаем дамп базы:
```
pg_dump -U postgres -d energy_drinks_db -Fc > /tmp/energy_drinks_db_backup.dump
```

4️⃣ Выходим из контейнера:
```
exit
```

5️⃣ Копируем дамп из контейнера на сервер:
```
docker cp energy-postgres-1:/tmp/energy_drinks_db_backup.dump ./energy_drinks_db_backup.dump
```

6️⃣ Скачиваем дамп на локальную машину:

👉 Windows (PowerShell):

```
scp user@server:./energy_drinks_db_backup.dump C:\Users\USER\Downloads\
```

👉 Linux/macOS:

```
scp user@server:./energy_drinks_db_backup.dump ~/Downloads/
```

7️⃣ Подключаемся снова к серверу и чистим временные файлы:

Удаляем бэкап на сервере:
``` 
rm ./energy_drinks_db_backup.dump  
``` 
Заходим в контейнер
``` 
docker exec -it energy-postgres-1 bash
```
Удаляем бэкап с контейнера
```
rm /tmp/energy_drinks_db_backup.dump
```

8️⃣ Выходим из контейнера:
```
exit
```

9️⃣ Проверить, существует ли бэкап еще на сервере
```
find / -type f -name "*energy_drink*" 2>/dev/null
```

---

### 📥 Восстановление из резервной копии

1️⃣ Проверить, существует ли бэкап уже на сервере
```
find / -type f -name "*energy_drink*" 2>/dev/null
```

2️⃣ Загружаем дамп на сервер:

👉 Windows (PowerShell):

```
scp C:\Users\USER\Downloads\energy_drinks_db_backup.dump user@server:./energy_drinks_db_backup.dump
```

👉 Linux/macOS:

```
scp -r ~/Downloads/energy_drinks_db_backup.dump user@server:./energy_drinks_db_backup.dump
```

3️⃣ Копируем дамп в контейнер:
```
docker cp ./energy_drinks_db_backup.dump energy-postgres-1:/tmp/energy_drinks_db_backup.dump
```

4️⃣ Удаляем старую базу и создаём новую:

Останавливаем бэк
```
docker stop energy-backend-1
```
Дропаем бдшку
```
docker exec -it energy-postgres-1 psql -U postgres -c "DROP DATABASE IF EXISTS energy_drinks_db;"
```
Запускаем заново бэк
```
docker start energy-backend-1
```
Пересоздаем бдшку
```
docker exec -it energy-postgres-1 psql -U postgres -c "CREATE DATABASE energy_drinks_db;"

```

5️⃣ Восстанавливаем базу из дампа:

```
docker exec -i energy-postgres-1 pg_restore -U postgres -d energy_drinks_db --verbose /tmp/energy_drinks_db_backup.dump
```

6️⃣ Подключаемся снова к серверу и чистим временные файлы:

Удаляем бэкап на сервере:
``` 
rm ./energy_drinks_db_backup.dump  
``` 
Заходим в контейнер
``` 
docker exec -it energy-postgres-1 bash
```
Удаляем бэкап с контейнера
```
rm /tmp/energy_drinks_db_backup.dump
```

7️⃣ Выходим из контейнера:
```
exit
```

8️⃣ Проверить, существует ли бэкап еще на сервере
```
find / -type f -name "*energy_drink*" 2>/dev/null
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


# База энов
## _Величайшая база энов в истории человечества_

Developed by Stylua Inc (c)
Developers 
- [Jenkneo](https://github.com/Jenkneo)
- [nuafirytiasewo](https://github.com/nuafirytiasewo)

💻 Languages and Tools :
[![Технологии](https://skillicons.dev/icons?i=fastapi,py,postgres)](https://skillicons.dev)

## Общая структура проекта

После скачивания проекта установите все зависимости
```sh
my_project/
│
├── alembic/
│   ├── env.py          # Главный файл для настройки миграций
│   ├── versions/       # Каталог для хранения файлов миграций
│
├── alembic.ini         # Конфигурационный файл Alembic
│
├── app/
│   ├── __init__.py     # Пустой файл, который делает директорию модулем Python
│   ├── main.py         # Точка входа приложения FastAPI
│   ├── models.py       # SQLAlchemy модели
│   ├── database.py     # Подключение к базе данных
│   ├── crud.py         # CRUD операции для работы с данными
│   ├── schemas.py      # Pydantic схемы для валидации данных
│   └── api.py          # Роуты (эндпоинты)
│
├── venv/               # Виртуальное окружение (рекомендуется)
├── requirements.txt    # Зависимости проекта
```

## Начальная настройка

После скачивания проекта установите все зависимости
```sh
pip install -r requirements.txt
```

Прежде чем запустить проект, необходимо выполнить миграции, а так же применить эти миграции на базе данных
```sh
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```
> Alembic необходим для корректного изменения 
> таблиц в базе данных. Если не применять этот
> модуль в своей работе, то все изменения таблиц
> и их связей придется прописывать вручную, либо
> же сносить базу данных полностью, а после
> создавать новую.

Теперь можно запустить проект.
```sh
uvicorn app.main:app --reload
```

## Alembic

Небольшая инфа по файлам:
 - `alembic.ini` настраивает подключение к базе данных
 - `env.py` связывает Alembic с моделями SQLAlchemy.
 
По командам:
 - `revision --autogenerate` автоматически генерирует миграции.
 - `upgrade head` применяет миграции к базе данных.

import os
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv
from app.core.config import DATABASE_URL

# Подключаем конфигурацию Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Импортируем базу и модели
from app.db.models.base import Base  # Импортируем Base из своего проекта
from app.db.models import *  # Импортируем ВСЕ модели, чтобы Alembic их увидел

target_metadata = Base.metadata # Alembic будет использовать метаданные моделей


def run_migrations_offline() -> None:
    """Запускаем миграции в оффлайн-режиме."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запускаем миграции в онлайн-режиме."""
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

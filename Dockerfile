# Используем официальный образ Python 3.13-slim как базовый, чтобы минимизировать размер
FROM python:3.13-slim

# Устанавливаем рабочую директорию /app внутри контейнера для размещения кода
WORKDIR /app

# Копируем файл зависимостей requirements.txt в рабочую директорию контейнера
COPY requirements.txt .

# Устанавливаем системные и Python-зависимости, а затем очищаем временные файлы
RUN apt-get update && \
    # Устанавливаем libpq-dev для работы с PostgreSQL, gcc и python3-dev для сборки модулей
    apt-get install -y --no-install-recommends libpq-dev gcc python3-dev && \
    # Обновляем pip до последней версии для корректной установки зависимостей
    pip install --no-cache-dir --upgrade pip && \
    # Устанавливаем Python-зависимости из requirements.txt без сохранения кэша
    pip install --no-cache-dir -r requirements.txt && \
    # Удаляем gcc и python3-dev после сборки, так как они больше не нужны
    apt-get purge -y --auto-remove gcc python3-dev && \
    # Удаляем кэш apt для уменьшения размера итогового образа
    rm -rf /var/lib/apt/lists/*

# Копируем весь исходный код приложения в рабочую директорию контейнера
COPY . .

# Запускаем приложение с помощью uvicorn, слушаем на всех интерфейсах на порту 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
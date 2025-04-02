# --- Этап сборки ---
FROM python:3.13-alpine as builder

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости для работы с базой данных
RUN apk add --no-cache \
    postgresql-dev \
    gcc \
    musl-dev

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Финальный образ ---
FROM python:3.13-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

RUN apk add --no-cache libpq

COPY --from=builder /install /usr/local

# Копируем весь код
COPY . .

# Запускаем бэкенд
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
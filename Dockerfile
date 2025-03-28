# Указываем Docker, чтобы использовать Python для бэкенда
FROM python:3.13

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости для работы с базой данных
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev

# Копируем файл зависимостей
COPY requirements.txt /app/requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Добавляем путь к локально установленным пакетам в переменную среды PATH
ENV PATH="/root/.local/bin:$PATH"

# Копируем весь код
COPY . /app

# Открываем порт 8000 для бэкенда
EXPOSE 8000

# Запускаем бэкенд
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

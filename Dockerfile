# Указываем Docker, чтобы использовать Python для бэкенда
FROM python:3.13

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Копируем весь код
COPY . /app

# Открываем порт 8000 для бэкенда
EXPOSE 8000

# Запускаем бэкенд
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

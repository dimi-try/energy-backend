from fastapi import FastAPI
from .api import router as api_router

app = FastAPI()

# Подключаем роуты
app.include_router(api_router)

# Пример главной страницы
@app.get("/")
def read_root():
    return {"Welcome to": "energy database!"}
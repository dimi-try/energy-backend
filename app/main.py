from fastapi import FastAPI
from .api import router as api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "https://handy-redbird-visually.ngrok-free.app",
    "http://localhost",  # Добавьте другие, если необходимо
    "http://127.0.0.1",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # использовать allow_origins=origins на продакшне
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(api_router)

# Пример главной страницы
@app.get("/")
def read_root():
    return {"Welcome to": "energy database!"}
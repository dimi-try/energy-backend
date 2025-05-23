from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_router

app = FastAPI()

origins = [
    "http://localhost",
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
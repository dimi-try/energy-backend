from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import api_router
from app.database import create_db, close_db
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    await create_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

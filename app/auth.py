import hmac
import hashlib
import time
import os
from fastapi import HTTPException
from jose import jwt, JWTError
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')


def create_access_token(data: dict, expires_delta: Optional[float] = None):
    to_encode = data.copy()
    expire = time.time() + expires_delta if expires_delta else time.time() + 3600
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def validate(hash_str, init_data):
    parsed_query = urllib.parse.parse_qs(init_data)
    init_data = sorted([chunk.split("=") for chunk in urllib.parse.unquote(init_data).split("&") if not chunk.startswith("hash=")], key=lambda x: x[0])
    init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])
    
    secret_key = hmac.new("WebAppData".encode(), BOT_TOKEN.encode(), hashlib.sha256).digest()
    data_check = hmac.new(secret_key, init_data.encode(), hashlib.sha256)
    
    return data_check.hexdigest() == hash_str

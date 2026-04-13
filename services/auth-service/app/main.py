import os
import json
import logging
import bcrypt
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import redis.asyncio as redis

from core_utils.security import create_access_token

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
FOUNDER_EMAIL = os.getenv("FOUNDER_EMAIL", "dummy@xyz.in")
FOUNDER_PASSWORD = os.getenv("FOUNDER_PASSWORD", "dummy123")[:72]

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_client.set("role_scopes:founder", json.dumps(["superadmin"]))
    
    founder_key = f"user:email:{FOUNDER_EMAIL}"
    if not await redis_client.exists(founder_key):
        logging.info(f"Initializing Founder account: {FOUNDER_EMAIL}")
        
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(FOUNDER_PASSWORD.encode('utf-8'), salt)
        
        founder_data = {
            "user_id": "usr_founder_001",
            "email": FOUNDER_EMAIL,
            "password": hashed.decode('utf-8'),
            "role_id": "founder",
            "is_active": "true"
        }
        await redis_client.set(founder_key, json.dumps(founder_data))
    
    yield
    await redis_client.aclose()

app = FastAPI(title="NexusOps Auth Service", lifespan=lifespan)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@app.post("/login")
async def login(credentials: LoginRequest):
    user_json = await redis_client.get(f"user:email:{credentials.email}")
    if not user_json:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_data = json.loads(user_json)
    
    password_bytes = credentials.password[:72].encode('utf-8')
    hashed_bytes = user_data["password"].encode('utf-8')
    
    if not bcrypt.checkpw(password_bytes, hashed_bytes):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user_data["user_id"], "role_id": user_data["role_id"]})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/health")
async def health():
    return {"status": "online"}
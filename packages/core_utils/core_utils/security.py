import os
from jose import JWTError, jwt
from typing import List
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def has_required_scope(user_scopes: List[str], required_scopes: List[str]) -> bool:
    if "superadmin" in user_scopes: 
        return True
        
    for required in required_scopes:
        if required not in user_scopes:
            resource = required.split(":")[0]
            if f"{resource}:*" not in user_scopes:
                return False
    return True
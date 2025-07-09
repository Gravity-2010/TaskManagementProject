from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
import jwt
import sqlite3

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    return conn

def fake_hash_password(password: str):
    return "hashed_" + password  # Matches the stored 'hashed_admin'

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/token")
async def login(username: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    user = conn.execute('SELECT id, username, hashed_password FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    if not user or fake_hash_password(password) != user["hashed_password"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"sub": username, "id": user["id"]}, access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        conn = get_db_connection()
        user = conn.execute('SELECT id FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user")
        return {"username": username, "id": user_id}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.routes import tasks
from app.routes.auth import router as auth_router, get_current_user, create_access_token, pwd_context
from fastapi.security import OAuth2PasswordBearer
import sqlite3

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.include_router(tasks.router)
app.include_router(auth_router)

def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": None})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    user = conn.execute('SELECT id, hashed_password FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    if not user or not pwd_context.verify(password, user['hashed_password']):
        return templates.TemplateResponse("index.html", {"request": request, "message": "Invalid username or password"})
    token = create_access_token({"sub": username, "id": user['id']})
    response = RedirectResponse(url="/tasks", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response

@app.get("/register")
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "message": None})

@app.post("/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    existing_user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    if existing_user:
        conn.close()
        return templates.TemplateResponse("register.html", {"request": request, "message": "Username already taken"})
    hashed_password = pwd_context.hash(password)
    conn.execute('INSERT INTO users (username, hashed_password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response

@app.get("/settings", tags=["settings"], include_in_schema=False)
async def settings_get(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("settings.html", {"request": request, "current_user": current_user})

@app.post("/settings/username")
async def update_username(new_username: str = Form(...), current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    existing_user = conn.execute('SELECT id FROM users WHERE username = ?', (new_username,)).fetchone()
    if existing_user:
        conn.close()
        raise HTTPException(status_code=400, detail="Username already taken")
    conn.execute('UPDATE users SET username = ? WHERE id = ?', (new_username, current_user["id"]))
    conn.commit()
    conn.close()

    token = create_access_token({"sub": new_username, "id": current_user["id"]})
    response = RedirectResponse(url="/tasks", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response

@app.post("/settings/theme")
async def update_theme(theme: str = Form(...), current_user: dict = Depends(get_current_user)):
    response = RedirectResponse(url="/settings", status_code=303)
    response.set_cookie(key="theme", value=theme, httponly=False)
    return response

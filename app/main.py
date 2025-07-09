from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from app.routes import tasks  # Import routes
from app.routes.auth import router as auth_router
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.include_router(tasks.router)  # Include task routes
app.include_router(auth_router)

@app.get("/")
async def home(request: Request, token: str = Depends(oauth2_scheme)):
    return templates.TemplateResponse("index.html", {"request": request})

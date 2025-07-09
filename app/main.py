from fastapi import FastAPI
from app.routes import tasks  # Import routes
from app.routes.auth import router as auth_router

app = FastAPI()

app.include_router(tasks.router)  # Include task routes
app.include_router(auth_router)

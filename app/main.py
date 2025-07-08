from fastapi import FastAPI
from app.routes import tasks  # Import routes

app = FastAPI()

app.include_router(tasks.router)  # Include task routes

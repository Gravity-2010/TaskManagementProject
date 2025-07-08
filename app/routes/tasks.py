from fastapi import APIRouter
from app.models import tasks  # Placeholder for models

router = APIRouter()

@router.get("/tasks", tags=["tasks"])
async def get_tasks():
    return [{"id": 1, "title": "Sample Task", "completed": False}]

from typing import Optional
from pydantic import BaseModel
# from app.models.tasks import Task, TaskCreate, CategoryCreate

class Task(BaseModel):
    id: int
    title: str
    completed: bool
    user_id: int
    category_id: Optional[int] = None

class TaskCreate(BaseModel):
    title: str
    completed: Optional[bool] = False
    category_id: Optional[int] = None

class CategoryCreate(BaseModel):
    name: str

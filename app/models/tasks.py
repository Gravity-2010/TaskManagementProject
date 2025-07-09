from typing import Optional
from pydantic import BaseModel

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

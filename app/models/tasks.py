from typing import Optional
from pydantic import BaseModel

class Task(BaseModel):
    id: int
    title: str
    completed: bool
    user_id: int

class TaskCreate(BaseModel):
    title: str
    completed: Optional[bool] = False

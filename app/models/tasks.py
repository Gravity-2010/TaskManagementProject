from typing import Optional
from pydantic import BaseModel

class Task(BaseModel):
    id: int
    title: str
    completed: bool

class TaskCreate(BaseModel):
    title: str
    completed: Optional[bool] = False

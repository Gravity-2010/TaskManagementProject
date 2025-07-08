from fastapi import APIRouter, HTTPException
from app.models.tasks import Task, TaskCreate
from typing import List

router = APIRouter()

# In-memory store (replace with database later)
tasks_db: List[Task] = []

@router.get("/tasks", tags=["tasks"])
async def get_tasks() -> List[Task]:
    return tasks_db

@router.get("/tasks/{task_id}", tags=["tasks"])
async def get_task(task_id: int) -> Task:
    for task in tasks_db:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@router.post("/tasks", tags=["tasks"])
async def create_task(task: TaskCreate) -> Task:
    new_id = len(tasks_db) + 1
    new_task = Task(id=new_id, **task.dict())
    tasks_db.append(new_task)
    return new_task

@router.put("/tasks/{task_id}", tags=["tasks"])
async def update_task(task_id: int, task: TaskCreate) -> Task:
    for i, t in enumerate(tasks_db):
        if t.id == task_id:
            updated_task = Task(id=task_id, **task.dict())
            tasks_db[i] = updated_task
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found")

@router.delete("/tasks/{task_id}", tags=["tasks"])
async def delete_task(task_id: int) -> dict:
    for i, t in enumerate(tasks_db):
        if t.id == task_id:
            tasks_db.pop(i)
            return {"message": "Task deleted"}
    raise HTTPException(status_code=404, detail="Task not found")

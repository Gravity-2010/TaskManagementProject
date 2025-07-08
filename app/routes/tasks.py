from fastapi import APIRouter, HTTPException
from app.models.tasks import Task, TaskCreate
from typing import List
import sqlite3

router = APIRouter()

def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    return conn

# In-memory store (replace with database later)
# tasks_db: List[Task] = []

@router.get("/tasks", tags=["tasks"])
async def get_tasks() -> List[Task]:
    conn = get_db_connection()
    tasks = conn.execute('SELECT id, title, completed FROM tasks').fetchall()
    conn.close()
    return [dict(task) for task in tasks]

@router.get("/tasks/{task_id}", tags=["tasks"])
async def get_task(task_id: int) -> Task:
    conn = get_db_connection()
    task = conn.execute('SELECT id, title, completed FROM tasks WHERE id = ?', (task_id,)).fetchone()
    conn.close()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(task)

@router.post("/tasks", tags=["tasks"])
async def create_task(task: TaskCreate) -> Task:
    conn = get_db_connection()
    conn.execute('INSERT INTO tasks (title, completed) VALUES (?, ?)', (task.title, 1 if task.completed else 0))
    conn.commit()
    task_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()  # Ensure closure
    return Task(id=task_id, title=task.title, completed=task.completed)

@router.put("/tasks/{task_id}", tags=["tasks"])
async def update_task(task_id: int, task: TaskCreate) -> Task:
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET title = ?, completed = ? WHERE id = ?', (task.title, task.completed, task_id))
    conn.commit()
    conn.close()
    updated_task = conn.execute('SELECT id, title, completed FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(updated_task)

@router.delete("/tasks/{task_id}", tags=["tasks"])
async def delete_task(task_id: int) -> dict:
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    cursor = conn.execute('SELECT COUNT(*) FROM tasks WHERE id = ?', (task_id,))
    count = cursor.fetchone()[0]
    conn.close()
    if count == 0:
        return {"message": "Task deleted"}
    raise HTTPException(status_code=404, detail="Task not found")

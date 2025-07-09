from fastapi import APIRouter, HTTPException, Depends
from app.models.tasks import Task, TaskCreate
from typing import List
import sqlite3
from .auth import get_current_user

router = APIRouter()

def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/tasks", tags=["tasks"])
async def get_tasks(current_user: dict = Depends(get_current_user)) -> List[Task]:
    conn = get_db_connection()
    tasks = conn.execute('SELECT id, title, completed, user_id, category_id FROM tasks WHERE user_id = ?', (current_user["id"],)).fetchall()
    conn.close()
    return [dict(task) for task in tasks]

@router.get("/tasks/{task_id}", tags=["tasks"])
async def get_task(task_id: int, current_user: dict = Depends(get_current_user)) -> Task:
    conn = get_db_connection()
    task = conn.execute('SELECT id, title, completed, user_id, category_id FROM tasks WHERE id = ? AND user_id = ?', (task_id, current_user["id"],)).fetchone()
    conn.close()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(task)

@router.post("/tasks", tags=["tasks"])
async def create_task(task: TaskCreate, current_user: dict = Depends(get_current_user)) -> Task:
    conn = get_db_connection()
    if task.category_id:
        category = conn.execute('SELECT id FROM categories WHERE id = ? AND user_id = ?', (task.category_id, current_user["id"],)).fetchone()
        if not category:
            conn.close()
            raise HTTPException(status_code=400, detail="Invalid category")
    conn.execute('INSERT INTO tasks (title, completed, user_id, category_id) VALUES (?, ?, ?, ?)', (task.title, 1 if task.completed else 0, current_user["id"], task.category_id))
    conn.commit()
    task_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()
    return Task(id=task_id, title=task.title, completed=task.completed, user_id=current_user["id"], category_id=task.category_id)

@router.put("/tasks/{task_id}", tags=["tasks"])
async def update_task(task_id: int, task: TaskCreate, current_user: dict = Depends(get_current_user)) -> Task:
    conn = get_db_connection()
    if task.category_id:
        category = conn.execute('SELECT id FROM categories WHERE id = ? AND user_id = ?', (task.category_id, current_user["id"],)).fetchone()
        if not category:
            conn.close()
            raise HTTPException(status_code=400, detail="Invalid category")
    conn.execute('UPDATE tasks SET title = ?, completed = ?, category_id = ? WHERE id = ? AND user_id = ?', (task.title, 1 if task.completed else 0, task.category_id, task_id, current_user["id"]))
    conn.commit()
    conn.close()
    updated_task = conn.execute('SELECT id, title, completed, user_id, category_id FROM tasks WHERE id = ? AND user_id = ?', (task_id, current_user["id"],)).fetchone()
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(updated_task)

@router.delete("/tasks/{task_id}", tags=["tasks"])
async def delete_task(task_id: int, current_user: dict = Depends(get_current_user)) -> dict:
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, current_user["id"],))
    conn.commit()
    cursor = conn.execute('SELECT COUNT(*) FROM tasks WHERE id = ? AND user_id = ?', (task_id, current_user["id"],))
    count = cursor.fetchone()[0]
    conn.close()
    if count == 0:
        return {"message": "Task deleted"}
    raise HTTPException(status_code=404, detail="Task not found")

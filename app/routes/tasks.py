from fastapi import APIRouter, HTTPException, Depends, Request, Form
from app.models.tasks import Task, TaskCreate, CategoryCreate
from typing import List
import sqlite3
from .auth import get_current_user
from fastapi.templating import Jinja2Templates
from starlette.requests import Request as StarletteRequest
from fastapi.responses import RedirectResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    return conn

@router.get("/tasks", tags=["tasks"], include_in_schema=False)
async def get_tasks_html(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return templates.TemplateResponse("error.html", {"request": request, "message": "Please log in"})
    from starlette.requests import HTTPConnection
    fake_request = HTTPConnection(scope={"type": "http", "headers": [("authorization", f"Bearer {token}".encode())]})
    current_user = await get_current_user(fake_request)
    conn = get_db_connection()
    tasks = conn.execute('SELECT id, title, completed, user_id, category_id FROM tasks WHERE user_id = ?', (current_user["id"],)).fetchall()
    categories = conn.execute('SELECT id, name FROM categories WHERE user_id = ?', (current_user["id"],)).fetchall()
    conn.close()
    return templates.TemplateResponse("tasks.html", {"request": request, "tasks": [dict(task) for task in tasks], "categories": [dict(category) for category in categories]})

@router.post("/tasks")
async def create_task(request: Request, title: str = Form(...), current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    conn.execute('INSERT INTO tasks (title, completed, user_id) VALUES (?, ?, ?)', (title, 0, current_user["id"]))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/tasks", status_code=303)

@router.post("/tasks/{task_id}/delete")
async def delete_task(task_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    task = conn.execute('SELECT user_id FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if not task or task['user_id'] != current_user["id"]:
        conn.close()
        raise HTTPException(status_code=403, detail="Unauthorized or task not found")
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/tasks", status_code=303)

@router.put("/tasks/{task_id}/complete")
async def complete_task(task_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    task = conn.execute('SELECT user_id FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if not task or task['user_id'] != current_user["id"]:
        conn.close()
        raise HTTPException(status_code=403, detail="Unauthorized or task not found")
    conn.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/tasks", status_code=303)

@router.post("/tasks/{task_id}/edit")
async def edit_task(task_id: int, new_title: str = Form(...), current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    task = conn.execute('SELECT user_id FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if not task or task['user_id'] != current_user["id"]:
        conn.close()
        raise HTTPException(status_code=403, detail="Unauthorized or task not found")
    conn.execute('UPDATE tasks SET title = ? WHERE id = ?', (new_title, task_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/tasks", status_code=303)

@router.post("/categories")
async def create_category(name: str = Form(...), current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    conn.execute('INSERT INTO categories (name, user_id) VALUES (?, ?)', (name, current_user["id"]))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/tasks", status_code=303)

@router.post("/tasks/{task_id}/assign_category")
async def assign_category(task_id: int, category_id: int = Form(...), current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    task = conn.execute('SELECT user_id FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if not task or task['user_id'] != current_user["id"]:
        conn.close()
        raise HTTPException(status_code=403, detail="Unauthorized or task not found")
    category = conn.execute('SELECT user_id FROM categories WHERE id = ?', (category_id,)).fetchone()
    if not category or category['user_id'] != current_user["id"]:
        conn.close()
        raise HTTPException(status_code=403, detail="Unauthorized or category not found")
    conn.execute('UPDATE tasks SET category_id = ? WHERE id = ?', (category_id, task_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/tasks", status_code=303)

@router.delete("/categories/{category_id}", tags=["categories"])
async def delete_category(category_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    category = conn.execute('SELECT user_id FROM categories WHERE id = ?', (category_id,)).fetchone()
    if not category or category['user_id'] != current_user["id"]:
        conn.close()
        raise HTTPException(status_code=403, detail="Unauthorized or category not found")
    # Check if any tasks are using this category
    tasks_using_category = conn.execute('SELECT id FROM tasks WHERE category_id = ?', (category_id,)).fetchone()
    if tasks_using_category:
        conn.close()
        raise HTTPException(status_code=400, detail="Cannot delete category with assigned tasks")
    conn.execute('DELETE FROM categories WHERE id = ?', (category_id,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/tasks", status_code=303)

# from fastapi import APIRouter, HTTPException, Depends, Request, Form
# from app.models.tasks import Task, TaskCreate, CategoryCreate
# from typing import List
# import sqlite3
# from .auth import get_current_user
# from fastapi.templating import Jinja2Templates
# from starlette.requests import Request as StarletteRequest
# from fastapi.responses import RedirectResponse

# router = APIRouter()
# templates = Jinja2Templates(directory="app/templates")

# def get_db_connection():
#     conn = sqlite3.connect('tasks.db')
#     conn.row_factory = sqlite3.Row
#     return conn

# @router.get("/tasks", tags=["tasks"], include_in_schema=False)
# async def get_tasks_html(request: Request):
#     token = request.cookies.get("access_token")
#     if not token:
#         return templates.TemplateResponse("error.html", {"request": request, "message": "Please log in"})
#     from starlette.requests import HTTPConnection
#     fake_request = HTTPConnection(scope={"type": "http", "headers": [("authorization", f"Bearer {token}".encode())]})
#     current_user = await get_current_user(fake_request)
#     conn = get_db_connection()
#     tasks = conn.execute('SELECT id, title, completed, user_id, category_id FROM tasks WHERE user_id = ?', (current_user["id"],)).fetchall()
#     conn.close()
#     return templates.TemplateResponse("tasks.html", {"request": request, "tasks": [dict(task) for task in tasks]})

# @router.post("/tasks")
# async def create_task(request: Request, title: str = Form(...), current_user: dict = Depends(get_current_user)):
#     conn = get_db_connection()
#     conn.execute('INSERT INTO tasks (title, completed, user_id) VALUES (?, ?, ?)', (title, 0, current_user["id"]))
#     conn.commit()
#     conn.close()
#     return RedirectResponse(url="/tasks", status_code=303)

# @router.post("/tasks/{task_id}/edit")
# async def edit_task(task_id: int, new_title: str = Form(...), current_user: dict = Depends(get_current_user)):
#     conn = get_db_connection()
#     task = conn.execute('SELECT user_id FROM tasks WHERE id = ?', (task_id,)).fetchone()
#     if not task or task['user_id'] != current_user["id"]:
#         conn.close()
#         raise HTTPException(status_code=403, detail="Unauthorized or task not found")
#     conn.execute('UPDATE tasks SET title = ? WHERE id = ?', (new_title, task_id))
#     conn.commit()
#     conn.close()
#     return RedirectResponse(url="/tasks", status_code=303)

# # @router.get("/tasks", tags=["tasks"], include_in_schema=False)
# # async def get_tasks_html(request: Request):
# #     token = request.cookies.get("access_token")
# #     if not token:
# #         return templates.TemplateResponse("error.html", {"request": request, "message": "Please log in"})
# #     from starlette.requests import HTTPConnection
# #     fake_request = HTTPConnection(scope={"type": "http", "headers": [("authorization", f"Bearer {token}".encode())]})
# #     current_user = await get_current_user(fake_request)
# #     conn = get_db_connection()
# #     tasks = conn.execute('SELECT id, title, completed, user_id, category_id FROM tasks WHERE user_id = ?', (current_user["id"],)).fetchall()
# #     conn.close()
# #     return templates.TemplateResponse("tasks.html", {"request": request, "tasks": [dict(task) for task in tasks]})

# @router.post("/categories", tags=["categories"])
# async def create_category(category: CategoryCreate, current_user: dict = Depends(get_current_user)):
#     conn = get_db_connection()
#     existing_category = conn.execute('SELECT id FROM categories WHERE name = ? AND user_id = ?', (category.name, current_user["id"],)).fetchone()
#     if existing_category:
#         conn.close()
#         raise HTTPException(status_code=400, detail="Category already exists")
#     conn.execute('INSERT INTO categories (name, user_id) VALUES (?, ?)', (category.name, current_user["id"]))
#     conn.commit()
#     category_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
#     conn.close()
#     return {"id": category_id, "name": category.name, "user_id": current_user["id"]}

# @router.get("/categories", tags=["categories"])
# async def get_categories(current_user: dict = Depends(get_current_user)) -> List[dict]:
#     conn = get_db_connection()
#     categories = conn.execute('SELECT id, name, user_id FROM categories WHERE user_id = ?', (current_user["id"],)).fetchall()
#     conn.close()
#     return [dict(category) for category in categories]

# @router.delete("/categories/{category_id}", tags=["categories"])
# async def delete_category(category_id: int, current_user: dict = Depends(get_current_user)):
#     conn = get_db_connection()
#     category = conn.execute('SELECT id FROM categories WHERE id = ? AND user_id = ?', (category_id, current_user["id"],)).fetchone()
#     if not category:
#         conn.close()
#         raise HTTPException(status_code=404, detail="Category not found")
#     conn.execute('DELETE FROM categories WHERE id = ? AND user_id = ?', (category_id, current_user["id"],))
#     conn.commit()
#     conn.close()
#     return {"message": "Category deleted"}

# @router.get("/tasks", tags=["tasks"])
# async def get_tasks(current_user: dict = Depends(get_current_user)) -> List[Task]:
#     conn = get_db_connection()
#     tasks = conn.execute('SELECT id, title, completed, user_id, category_id FROM tasks WHERE user_id = ?', (current_user["id"],)).fetchall()
#     conn.close()
#     return [dict(task) for task in tasks]

# @router.get("/tasks/{task_id}", tags=["tasks"])
# async def get_task(task_id: int, current_user: dict = Depends(get_current_user)) -> Task:
#     conn = get_db_connection()
#     task = conn.execute('SELECT id, title, completed, user_id, category_id FROM tasks WHERE id = ? AND user_id = ?', (task_id, current_user["id"],)).fetchone()
#     conn.close()
#     if task is None:
#         raise HTTPException(status_code=404, detail="Task not found")
#     return dict(task)

# @router.post("/tasks", tags=["tasks"])
# async def create_task(task: TaskCreate, current_user: dict = Depends(get_current_user)) -> Task:
#     conn = get_db_connection()
#     if task.category_id:
#         category = conn.execute('SELECT id FROM categories WHERE id = ? AND user_id = ?', (task.category_id, current_user["id"],)).fetchone()
#         if not category:
#             conn.close()
#             raise HTTPException(status_code=400, detail="Invalid category")
#     conn.execute('INSERT INTO tasks (title, completed, user_id, category_id) VALUES (?, ?, ?, ?)', (task.title, 1 if task.completed else 0, current_user["id"], task.category_id))
#     conn.commit()
#     task_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
#     conn.close()
#     return Task(id=task_id, title=task.title, completed=task.completed, user_id=current_user["id"], category_id=task.category_id)

# @router.put("/tasks/{task_id}", tags=["tasks"])
# async def update_task(task_id: int, task: TaskCreate, current_user: dict = Depends(get_current_user)) -> Task:
#     conn = get_db_connection()
#     if task.category_id:
#         category = conn.execute('SELECT id FROM categories WHERE id = ? AND user_id = ?', (task.category_id, current_user["id"],)).fetchone()
#         if not category:
#             conn.close()
#             raise HTTPException(status_code=400, detail="Invalid category")
#     conn.execute('UPDATE tasks SET title = ?, completed = ?, category_id = ? WHERE id = ? AND user_id = ?', (task.title, 1 if task.completed else 0, task.category_id, task_id, current_user["id"]))
#     conn.commit()
#     conn.close()
#     updated_task = conn.execute('SELECT id, title, completed, user_id, category_id FROM tasks WHERE id = ? AND user_id = ?', (task_id, current_user["id"],)).fetchone()
#     if updated_task is None:
#         raise HTTPException(status_code=404, detail="Task not found")
#     return dict(updated_task)

# @router.delete("/tasks/{task_id}", tags=["tasks"])
# async def delete_task(task_id: int, current_user: dict = Depends(get_current_user)) -> dict:
#     conn = get_db_connection()
#     conn.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, current_user["id"],))
#     conn.commit()
#     cursor = conn.execute('SELECT COUNT(*) FROM tasks WHERE id = ? AND user_id = ?', (task_id, current_user["id"],))
#     count = cursor.fetchone()[0]
#     conn.close()
#     if count == 0:
#         return {"message": "Task deleted"}
#     raise HTTPException(status_code=404, detail="Task not found")

# # ... (previous imports and router definition remain)

# @router.put("/tasks/{task_id}/complete", tags=["tasks"])
# async def complete_task(task_id: int, current_user: dict = Depends(get_current_user)) -> Task:
#     conn = get_db_connection()
#     task = conn.execute('SELECT id, title, completed, user_id, category_id FROM tasks WHERE id = ? AND user_id = ?', (task_id, current_user["id"],)).fetchone()
#     if task is None:
#         conn.close()
#         raise HTTPException(status_code=404, detail="Task not found")
#     conn.execute('UPDATE tasks SET completed = 1 WHERE id = ? AND user_id = ?', (task_id, current_user["id"]))
#     conn.commit()
#     conn.close()
#     return dict(task._replace(completed=1))

# @router.post("/tasks/{task_id}/delete", tags=["tasks"])
# async def delete_task(task_id: int, current_user: dict = Depends(get_current_user)) -> dict:
#     conn = get_db_connection()
#     conn.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, current_user["id"],))
#     conn.commit()
#     cursor = conn.execute('SELECT COUNT(*) FROM tasks WHERE id = ? AND user_id = ?', (task_id, current_user["id"],))
#     count = cursor.fetchone()[0]
#     conn.close()
#     if count == 0:
#         return {"message": "Task deleted"}
#     raise HTTPException(status_code=404, detail="Task not found")

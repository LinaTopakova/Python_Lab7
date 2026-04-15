import asyncio
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.redis_storage import storage          # <-- изменён импорт
from app.tasks import long_running_task, sync_cpu_bound
from app.queue import task_queue
from app.logger import logger

# Роутер для нотификаций (без изменений)
notify_router = APIRouter(prefix="/notify", tags=["notifications"])

def send_email(email: str, message: str):
    import time
    time.sleep(2)
    logger.info(f"Email sent to {email}: {message}")

@notify_router.post("/email")
async def notify_email(email: str, message: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email, message)
    return {"status": "email will be sent in background"}

# Роутер для длительных задач
tasks_router = APIRouter(prefix="/tasks", tags=["long tasks"])

@tasks_router.post("/process")
async def start_processing(input_data: dict, callback_url: Optional[str] = None):
    task_id = await storage.create_task(callback_url)   # <-- асинхронный вызов
    logger.info(f"Task created: {task_id}, callback_url: {callback_url}, input: {input_data}")
    task_queue.add_task(long_running_task, task_id, input_data)
    return {"task_id": task_id, "queued": True}

@tasks_router.get("/{task_id}")
async def get_task_status(task_id: str):
    task = await storage.get_task(task_id)  
    if not task:
        logger.warning(f"Task not found: {task_id}")
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@tasks_router.post("/compute")
async def compute_sync(data: dict):
    logger.info(f"CPU-bound computation requested with data: {data}")
    result = await asyncio.to_thread(sync_cpu_bound, data)
    return result
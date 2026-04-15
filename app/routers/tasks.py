import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.storage import create_task, get_task
from app.tasks import long_running_task, sync_cpu_bound
from app.queue import task_queue
from typing import Optional

notify_router = APIRouter(prefix="/notify", tags=["notifications"])

def send_email(email: str, message: str):
    import time
    time.sleep(2)
    print(f"Email sent to {email}: {message}")

@notify_router.post("/email")
async def notify_email(email: str, message: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email, message)
    return {"status": "email will be sent in background"}

tasks_router = APIRouter(prefix="/tasks", tags=["long tasks"])

@tasks_router.post("/process")
async def start_processing(input_data: dict, callback_url: Optional[str] = None):
    task_id = create_task(callback_url)
    task_queue.add_task(long_running_task, task_id, input_data)
    return {"task_id": task_id, "queued": True}


@tasks_router.get("/{task_id}")
async def get_task_status(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@tasks_router.post("/compute")
async def compute_sync(data: dict):
    result = await asyncio.to_thread(sync_cpu_bound, data)
    return result





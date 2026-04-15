from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.storage import create_task, get_task
from app.tasks import long_running_task

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
async def start_processing(input_data: dict, background_tasks: BackgroundTasks):
    task_id = create_task()
    background_tasks.add_task(long_running_task, task_id, input_data)
    return {"task_id": task_id}

@tasks_router.get("/{task_id}")
async def get_task_status(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
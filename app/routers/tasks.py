from fastapi import APIRouter, BackgroundTasks

router = APIRouter(prefix="/notify", tags=["notifications"])

def send_email(email: str, message: str):
    # Имитация отправки email (синхронная операция)
    import time
    time.sleep(2)  # симуляция работы SMTP
    print(f"Email sent to {email}: {message}")

@router.post("/email")
async def notify_email(email: str, message: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email, message)
    return {"status": "email will be sent in background"}
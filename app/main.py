from fastapi import FastAPI
from app.config import settings
from app.routers import notify_router, tasks_router, websocket_router
from app.queue import task_queue

app = FastAPI(title=settings.app_name)

app.include_router(notify_router)
app.include_router(tasks_router)
app.include_router(websocket_router)

@app.on_event("startup")
async def startup_event():
    await task_queue.start()

@app.on_event("shutdown")
async def shutdown_event():
    await task_queue.stop()

@app.get("/")
async def root():
    return {"message": "Hello, Async FastAPI!"}
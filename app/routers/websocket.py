from fastapi import APIRouter

websocket_router = APIRouter(prefix="/ws", tags=["websocket"])
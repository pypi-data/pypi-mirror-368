from fastapi import APIRouter

from . import chat, run


api_router = APIRouter()

# Grouped routers
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(run.router, prefix="/run", tags=["run"])

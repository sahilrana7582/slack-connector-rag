from fastapi import APIRouter

from app.routes import rag, slack

api_router = APIRouter()
api_router.include_router(slack.router)
api_router.include_router(rag.router)

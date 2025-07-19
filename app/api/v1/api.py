from fastapi import APIRouter
from app.api.v1.endpoints import caption

api_router = APIRouter()
api_router.include_router(caption.router, prefix="/caption", tags=["Caption Generator"])

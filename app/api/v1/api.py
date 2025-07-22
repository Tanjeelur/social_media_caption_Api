from fastapi import APIRouter
from app.api.v1.endpoints import caption

api_router = APIRouter()
api_router.include_router(caption.router, prefix="/caption", tags=["Caption Generator"])
#api_router.include_router(re_generate_caption.router, prefix="/re_generate_caption", tags=["Re generate caption"])

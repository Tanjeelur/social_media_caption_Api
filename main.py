from fastapi import FastAPI
from app.api.v1.api import api_router

app = FastAPI(title="Caption Generator")

# Register API routes
app.include_router(api_router, prefix="/api/v1")


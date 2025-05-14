from fastapi import APIRouter
from app.api.v1.endpoints import users

router = APIRouter(prefix="/api/v1")

router.include_router(users.router, tags=["Access"])
# app/api/router.py
from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.rooms import router as rooms_router
from app.api.routes.bookings import router as bookings_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(rooms_router)
api_router.include_router(bookings_router)

# Luxora-Backend/app/main.py
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.cors import add_cors_middleware
from app.db.init_db import init_db

logger = logging.getLogger("luxora")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once on startup and once on shutdown.
    We create database tables on startup for SQLite development.
    """
    init_db()
    logger.info("🚀 Luxora API started successfully")
    yield
    logger.info("🛑 Luxora API shutdown complete")


# IMPORTANT:
# Uvicorn expects a top-level variable named `app` in this module.
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS middleware
add_cors_middleware(app)

# API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["root"])
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "status": "active",
    }


@app.get(f"{settings.API_V1_PREFIX}/health", tags=["health"])
async def health_check():
    return {"status": "healthy", "message": "API is running smoothly"}

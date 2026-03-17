"""
To-Do List API - Main Application Entry Point
"""

from fastapi import FastAPI
from app.core import settings
from app.routers import todo_router
from app.routers.auth import router as auth_router
from app.routers.tag import router as tag_router
from app.db import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="A simple to-do list API with database persistence",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# Include routers
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(todo_router, prefix=settings.API_PREFIX)
app.include_router(tag_router, prefix=settings.API_PREFIX)


@app.get("/")
def read_root():
    """Welcome endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "api_prefix": settings.API_PREFIX,
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )

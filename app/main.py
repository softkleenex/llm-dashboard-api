from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.db.connection import init_pool, close_pool, test_connection
from app.routers import department, user, session

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initializing database connection pool...")
    init_pool()
    if test_connection():
        print("Database connection successful!")
    else:
        print("Warning: Database connection failed!")
    yield
    # Shutdown
    print("Closing database connection pool...")
    close_pool()


app = FastAPI(
    title="LLM Dashboard API",
    description="LLM 관리 대시보드 백엔드 API (Phase 4)",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(department.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
app.include_router(session.router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": "LLM Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    db_status = test_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )

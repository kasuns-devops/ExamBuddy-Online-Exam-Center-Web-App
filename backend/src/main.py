"""
ExamBuddy Backend - FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from src.config import settings
from src.middleware.error_handler import register_error_handlers

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="ExamBuddy Online Exam Center Platform - Backend API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register error handlers
register_error_handlers(app)

# Register API routers (to be added in Phase 3)
# from src.api import auth, projects, questions, exams, results
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
# app.include_router(questions.router, prefix="/api/questions", tags=["Questions"])
# app.include_router(exams.router, prefix="/api/exams", tags=["Exams"])
# app.include_router(results.router, prefix="/api/results", tags=["Results"])


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "ExamBuddy API",
        "version": settings.app_version,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }


# Lambda handler using Mangum
handler = Mangum(app, lifespan="off")

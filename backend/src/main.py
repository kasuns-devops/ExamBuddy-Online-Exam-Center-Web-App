"""
ExamBuddy Backend - FastAPI Application Entry Point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import json
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

# Add middleware to ensure CORS headers are always present
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    """Add CORS headers to all responses"""
    if request.method == "OPTIONS":
        return JSONResponse(
            content={},
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            }
        )
    
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# Configure CORS middleware (as fallback)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
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


@app.options("/")
async def root_options():
    """OPTIONS endpoint for CORS preflight"""
    # This will be handled by middleware
    return {}


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }


# Catch-all OPTIONS for any path (CORS preflight)
@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle CORS preflight for all paths"""
    # This will be handled by middleware
    return {}


# Lambda handler using Mangum
handler = Mangum(app, lifespan="off")

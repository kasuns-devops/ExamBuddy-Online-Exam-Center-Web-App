"""
ExamBuddy Backend - FastAPI Application Entry Point
"""
import sys
from typing import Any, Dict

# Try to import FastAPI/Mangum - if they fail, use fallback handler
try:
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    from mangum import Mangum
    from src.config import settings
    from src.middleware.error_handler import register_error_handlers
    FASTAPI_AVAILABLE = True
except ImportError as e:
    FASTAPI_AVAILABLE = False


if FASTAPI_AVAILABLE:
    # Initialize FastAPI app
    app = FastAPI(
        title="ExamBuddy API",
        version="0.1.0",
        description="ExamBuddy Online Exam Center Platform - Backend API",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Custom middleware to add CORS headers - MUST be first
    @app.middleware("http")
    async def add_cors_headers(request: Request, call_next):
        """Add CORS headers to all responses - handles both preflight and actual requests"""
        # Handle OPTIONS (preflight) requests
        if request.method == "OPTIONS":
            return JSONResponse(
                content={},
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization",
                    "Access-Control-Max-Age": "3600",
                }
            )
        
        # Process actual request
        try:
            response = await call_next(request)
        except Exception as e:
            # Even error responses need CORS headers
            response = JSONResponse(
                status_code=500,
                content={"detail": str(e)},
            )
        
        # Add CORS headers to response
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

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
            "version": "0.1.0",
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
            "app": "ExamBuddy API",
            "version": "0.1.0"
        }

    # Catch-all OPTIONS for any path (CORS preflight)
    @app.options("/{path:path}")
    async def options_handler(path: str):
        """Handle CORS preflight for all paths"""
        # This will be handled by middleware
        return {}

    # Lambda handler using Mangum
    handler = Mangum(app, lifespan="off")

else:
    # Fallback raw handler if FastAPI/Mangum not available
    def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Raw Lambda handler - returns CORS responses without FastAPI"""
        method = (
            event.get('requestContext', {}).get('http', {}).get('method')
            or event.get('httpMethod')
            or 'GET'
        )
        path = event.get('rawPath') or event.get('path') or '/'

        cors_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Max-Age': '3600',
            'Content-Type': 'application/json',
        }
        
        # Handle OPTIONS (preflight)
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': ''
            }
        
        # Handle GET / (root health check)
        if method == 'GET' and path == '/':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': '{"message":"ExamBuddy API","version":"0.1.0","status":"healthy"}'
            }
        
        # Handle GET /health
        if method == 'GET' and path == '/health':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': '{"status":"healthy","app":"ExamBuddy API","version":"0.1.0"}'
            }
        
        # Not found
        return {
            'statusCode': 404,
            'headers': cors_headers,
            'body': '{"detail":"Not Found"}'
        }

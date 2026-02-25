"""
ExamBuddy Backend - FastAPI Application Entry Point
"""
import sys
import json
import uuid
import base64
import time
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
    FALLBACK_QUESTIONS = [
        {
            "question_id": "q-sample-1",
            "text": "What is 2 + 2?",
            "answer_options": ["3", "4", "5", "6"],
            "correct_answer_index": 1,
            "project_id": "default"
        }
    ]

    def _get_header(headers: Dict[str, Any], key: str) -> str:
        if not headers:
            return ""
        return headers.get(key) or headers.get(key.lower()) or headers.get(key.title()) or ""

    def _is_authorized(headers: Dict[str, Any]) -> bool:
        auth_header = _get_header(headers, 'Authorization')
        if not auth_header.startswith('Bearer '):
            return False

        token = auth_header.split(' ', 1)[1].strip()
        parts = token.split('.')
        if len(parts) != 3:
            return False

        try:
            payload_b64 = parts[1] + '=' * (-len(parts[1]) % 4)
            payload_raw = base64.urlsafe_b64decode(payload_b64.encode('utf-8')).decode('utf-8')
            payload = json.loads(payload_raw)

            exp = payload.get('exp')
            token_use = payload.get('token_use')

            if exp and int(exp) < int(time.time()):
                return False
            if token_use and token_use not in ('id', 'access'):
                return False
            return True
        except Exception:
            return False

    def _parse_json_body(event: Dict[str, Any]) -> Dict[str, Any]:
        body = event.get('body')
        if not body:
            return {}
        if event.get('isBase64Encoded'):
            body = base64.b64decode(body).decode('utf-8')
        if isinstance(body, dict):
            return body
        return json.loads(body)

    # Fallback raw handler if FastAPI/Mangum not available
    def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Raw Lambda handler - returns CORS responses without FastAPI"""
        method = (
            event.get('requestContext', {}).get('http', {}).get('method')
            or event.get('httpMethod')
            or 'GET'
        )
        path = event.get('rawPath') or event.get('path') or '/'
        headers = event.get('headers') or {}
        query = event.get('queryStringParameters') or {}

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

        # Protected: GET /api/questions
        if method == 'GET' and path == '/api/questions':
            if not _is_authorized(headers):
                return {
                    'statusCode': 401,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'Unauthorized'})
                }

            project_id = query.get('project_id')
            items = FALLBACK_QUESTIONS
            if project_id:
                items = [item for item in FALLBACK_QUESTIONS if item.get('project_id') == project_id]

            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({'items': items, 'count': len(items)})
            }

        # Protected: POST /api/questions
        if method == 'POST' and path == '/api/questions':
            if not _is_authorized(headers):
                return {
                    'statusCode': 401,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'Unauthorized'})
                }

            try:
                payload = _parse_json_body(event)
            except Exception:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'Invalid JSON body'})
                }

            text = (payload.get('text') or '').strip()
            answer_options = payload.get('answer_options') or []
            correct_answer_index = payload.get('correct_answer_index', 0)
            project_id = payload.get('project_id', 'default')

            if not text or not isinstance(answer_options, list) or len(answer_options) < 2:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'text and at least 2 answer_options are required'})
                }

            if not isinstance(correct_answer_index, int) or correct_answer_index < 0 or correct_answer_index >= len(answer_options):
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'correct_answer_index is out of range'})
                }

            question = {
                'question_id': f"q-{uuid.uuid4().hex[:8]}",
                'text': text,
                'answer_options': answer_options,
                'correct_answer_index': correct_answer_index,
                'project_id': project_id,
            }
            FALLBACK_QUESTIONS.append(question)

            return {
                'statusCode': 201,
                'headers': cors_headers,
                'body': json.dumps(question)
            }
        
        # Not found
        return {
            'statusCode': 404,
            'headers': cors_headers,
            'body': '{"detail":"Not Found"}'
        }

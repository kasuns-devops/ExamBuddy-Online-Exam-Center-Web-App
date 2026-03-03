"""
ExamBuddy Backend - FastAPI Application Entry Point
"""
import sys
import json
import uuid
import base64
import time
import random
import copy
from typing import Any, Dict

# Try to import FastAPI/Mangum - if they fail (including config errors), use fallback handler
try:
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    from mangum import Mangum
    from src.config import settings
    from src.middleware.error_handler import register_error_handlers
    FASTAPI_AVAILABLE = True
except Exception:
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
            "project_id": "default",
            "difficulty": "easy",
            "question_type": "single_choice"
        },
        {
            "question_id": "q-sample-2",
            "text": "The Earth is flat.",
            "answer_options": ["False", "True"],
            "correct_answer_index": 0,
            "project_id": "default",
            "difficulty": "easy",
            "question_type": "true_false",
            "metadata": {
                "options": ["False", "True"]
            }
        },
        {
            "question_id": "q-sample-3",
            "text": "HTTP stands for ___ Transfer Protocol.",
            "answer_options": ["Correct", "Incorrect"],
            "correct_answer_index": 0,
            "project_id": "default",
            "difficulty": "medium",
            "question_type": "fill_in_blank",
            "metadata": {
                "expected_text": "HyperText"
            }
        },
        {
            "question_id": "q-sample-4",
            "text": "What does HTTP stand for?",
            "answer_options": ["Correct selection", "Incorrect selection"],
            "correct_answer_index": 0,
            "project_id": "default",
            "difficulty": "easy",
            "question_type": "multiple_response",
            "metadata": {
                "choices": [
                    "HyperText Transfer Protocol",
                    "HighText Transfer Process",
                    "Hyper Transfer Text Program",
                    "Home Tool Transfer Protocol"
                ],
                "correct_indices": [0]
            }
        },
        {
            "question_id": "q-sample-5",
            "text": "In SQL, which clause is used to filter grouped records?",
            "answer_options": ["All pairs correct", "At least one pair incorrect"],
            "correct_answer_index": 0,
            "project_id": "default",
            "difficulty": "medium",
            "question_type": "matching",
            "metadata": {
                "left_items": ["WHERE", "HAVING", "ORDER BY"],
                "right_items": ["Sort result set", "Filter grouped records", "Filter rows before grouping"],
                "correct_pairs": {
                    "WHERE": "Filter rows before grouping",
                    "HAVING": "Filter grouped records",
                    "ORDER BY": "Sort result set"
                }
            }
        },
        {
            "question_id": "q-sample-6",
            "text": "Which AWS service is object storage?",
            "answer_options": ["Correct order", "Incorrect order"],
            "correct_answer_index": 0,
            "project_id": "default",
            "difficulty": "easy",
            "question_type": "ordering",
            "metadata": {
                "items": ["Draft requirements", "Design solution", "Implement", "Test and verify"],
                "correct_order": ["Draft requirements", "Design solution", "Implement", "Test and verify"]
            }
        },
        {
            "question_id": "q-sample-7",
            "text": "Which algorithm typically has O(log n) search time on sorted data?",
            "answer_options": ["Correct area", "Incorrect area"],
            "correct_answer_index": 0,
            "project_id": "default",
            "difficulty": "medium",
            "question_type": "hotspot",
            "metadata": {
                "hotspots": ["A", "B", "C", "D"],
                "correct_hotspot": "B"
            }
        },
        {
            "question_id": "q-sample-8",
            "text": "What is the primary purpose of JWT in web applications?",
            "answer_options": ["Correct build list", "Incorrect build list"],
            "correct_answer_index": 0,
            "project_id": "default",
            "difficulty": "medium",
            "question_type": "build_list",
            "metadata": {
                "items": ["Open login page", "Submit credentials", "Receive token", "Call protected API"],
                "correct_order": ["Open login page", "Submit credentials", "Receive token", "Call protected API"]
            }
        },
        {
            "question_id": "q-sample-9",
            "text": "Which CAP theorem trade-off is common in globally distributed NoSQL systems?",
            "answer_options": ["CP only", "CA only", "AP tendency", "None"],
            "correct_answer_index": 2,
            "project_id": "default",
            "difficulty": "hard",
            "question_type": "scenario",
            "metadata": {
                "scenario": "A globally distributed service prioritizes availability during network partitions."
            }
        },
        {
            "question_id": "q-sample-10",
            "text": "You need to deploy a serverless REST API with minimum ops overhead. Best fit?",
            "answer_options": [
                "EC2 + Nginx",
                "Lambda + API Gateway",
                "ECS on EC2",
                "Bare metal VM"
            ],
            "correct_answer_index": 1,
            "project_id": "default",
            "difficulty": "hard",
            "question_type": "scenario"
        }
    ]
    FALLBACK_EXAM_SESSIONS: Dict[str, Dict[str, Any]] = {}

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

    def _build_correct_answer_payload(question: Dict[str, Any]) -> Dict[str, Any]:
        question_type = question.get('question_type', 'single_choice')
        metadata = question.get('metadata') or {}
        answer_options = question.get('answer_options') or []
        correct_index = question.get('correct_answer_index')

        if question_type == 'fill_in_blank':
            expected_text = (metadata.get('expected_text') or '').strip()
            return {
                'type': question_type,
                'text': expected_text,
                'display': expected_text,
            }

        if question_type == 'multiple_response':
            correct_indices = metadata.get('correct_indices') or ([] if correct_index is None else [correct_index])
            correct_labels = []
            choices = metadata.get('choices') or answer_options
            for idx in correct_indices:
                try:
                    correct_labels.append(choices[int(idx)])
                except Exception:
                    pass
            return {
                'type': question_type,
                'indices': correct_indices,
                'labels': correct_labels,
                'display': ', '.join(correct_labels),
            }

        if question_type in ('ordering', 'build_list'):
            correct_order = metadata.get('correct_order') or []
            return {
                'type': question_type,
                'items': correct_order,
                'display': ' -> '.join(correct_order),
            }

        if question_type == 'matching':
            correct_pairs = metadata.get('correct_pairs') or {}
            pair_strings = [f"{k} -> {v}" for k, v in correct_pairs.items()]
            return {
                'type': question_type,
                'pairs': correct_pairs,
                'display': '; '.join(pair_strings),
            }

        if question_type == 'hotspot':
            spot = metadata.get('correct_hotspot')
            return {
                'type': question_type,
                'spot': spot,
                'display': str(spot) if spot is not None else '',
            }

        label = None
        if correct_index is not None:
            try:
                label = answer_options[int(correct_index)]
            except Exception:
                label = None

        return {
            'type': question_type,
            'index': correct_index,
            'label': label,
            'display': label if label is not None else str(correct_index),
        }

    def _evaluate_answer(question: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        question_type = question.get('question_type', 'single_choice')
        metadata = question.get('metadata') or {}
        answer_options = question.get('answer_options') or []
        correct_index = question.get('correct_answer_index')

        selected_answer = None
        selected_display = ''
        is_correct = False
        accepted = False

        if question_type == 'fill_in_blank':
            answer_text = (payload.get('answer_text') or '').strip()
            expected_text = (metadata.get('expected_text') or '').strip()
            accepted = len(answer_text) > 0
            is_correct = accepted and answer_text.lower() == expected_text.lower()
            selected_answer = {'text': answer_text}
            selected_display = answer_text

        elif question_type == 'multiple_response':
            selected_indices = payload.get('selected_indices') or []
            normalized_selected = sorted({int(i) for i in selected_indices}) if isinstance(selected_indices, list) else []
            correct_indices = metadata.get('correct_indices') or ([] if correct_index is None else [int(correct_index)])
            normalized_correct = sorted({int(i) for i in correct_indices})
            accepted = len(normalized_selected) > 0
            is_correct = accepted and normalized_selected == normalized_correct
            labels = []
            choices = metadata.get('choices') or answer_options
            for idx in normalized_selected:
                try:
                    labels.append(choices[idx])
                except Exception:
                    pass
            selected_answer = {'indices': normalized_selected, 'labels': labels}
            selected_display = ', '.join(labels)

        elif question_type in ('ordering', 'build_list'):
            ordered_items = payload.get('ordered_items') or []
            if not isinstance(ordered_items, list):
                ordered_items = []
            correct_order = metadata.get('correct_order') or []
            accepted = len(ordered_items) > 0
            is_correct = accepted and ordered_items == correct_order
            selected_answer = {'items': ordered_items}
            selected_display = ' -> '.join(ordered_items)

        elif question_type == 'matching':
            selected_matches = payload.get('selected_matches') or {}
            if not isinstance(selected_matches, dict):
                selected_matches = {}
            correct_pairs = metadata.get('correct_pairs') or {}
            accepted = len(selected_matches) > 0
            is_correct = accepted and selected_matches == correct_pairs
            selected_answer = {'pairs': selected_matches}
            selected_display = '; '.join([f"{k} -> {v}" for k, v in selected_matches.items()])

        elif question_type == 'hotspot':
            selected_hotspot = payload.get('selected_hotspot')
            correct_hotspot = metadata.get('correct_hotspot')
            accepted = selected_hotspot is not None and str(selected_hotspot).strip() != ''
            is_correct = accepted and str(selected_hotspot) == str(correct_hotspot)
            selected_answer = {'spot': selected_hotspot}
            selected_display = str(selected_hotspot) if selected_hotspot is not None else ''

        else:
            answer_index = payload.get('answer_index')
            if answer_index is not None:
                try:
                    answer_index = int(answer_index)
                    accepted = True
                    is_correct = answer_index == int(correct_index)
                    selected_answer = {'index': answer_index}
                    if 0 <= answer_index < len(answer_options):
                        selected_answer['label'] = answer_options[answer_index]
                        selected_display = answer_options[answer_index]
                    else:
                        selected_display = str(answer_index)
                except Exception:
                    accepted = False

        return {
            'question_type': question_type,
            'accepted': accepted,
            'is_correct': is_correct,
            'selected_answer': selected_answer,
            'selected_display': selected_display,
            'correct_answer': _build_correct_answer_payload(question),
        }

    def _shuffle_question_options(question: Dict[str, Any]) -> Dict[str, Any]:
        shuffled = copy.deepcopy(question)
        question_type = shuffled.get('question_type', 'single_choice')

        # Shuffle classic answer options while preserving correct answer mapping
        options = shuffled.get('answer_options')
        correct_index = shuffled.get('correct_answer_index')
        if (
            isinstance(options, list)
            and len(options) > 1
            and correct_index is not None
            and question_type in ('single_choice', 'scenario', 'true_false')
        ):
            order = list(range(len(options)))
            random.shuffle(order)
            shuffled['answer_options'] = [options[i] for i in order]
            try:
                shuffled['correct_answer_index'] = order.index(int(correct_index))
            except Exception:
                pass

        # Shuffle multiple-response choices and remap correct indices
        if question_type == 'multiple_response':
            metadata = shuffled.get('metadata') or {}
            choices = metadata.get('choices')
            if isinstance(choices, list) and len(choices) > 1:
                order = list(range(len(choices)))
                random.shuffle(order)
                metadata['choices'] = [choices[i] for i in order]

                original_correct = metadata.get('correct_indices')
                if not isinstance(original_correct, list):
                    fallback_index = shuffled.get('correct_answer_index')
                    original_correct = [] if fallback_index is None else [fallback_index]

                remapped_correct = []
                for idx in original_correct:
                    try:
                        idx_int = int(idx)
                        if 0 <= idx_int < len(choices):
                            remapped_correct.append(order.index(idx_int))
                    except Exception:
                        continue

                metadata['correct_indices'] = sorted(remapped_correct)
                shuffled['metadata'] = metadata

        return shuffled

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

        # Protected: POST /api/exams/start
        if method == 'POST' and path == '/api/exams/start':
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

            project_id = payload.get('project_id', 'default')
            mode = payload.get('mode', 'test')
            requested_count = int(payload.get('question_count', 5))

            project_questions = [q for q in FALLBACK_QUESTIONS if q.get('project_id') == project_id]
            if not project_questions:
                project_questions = FALLBACK_QUESTIONS

            if not project_questions:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'No questions available'})
                }

            count = min(max(requested_count, 1), len(project_questions))
            selected_questions = [
                _shuffle_question_options(question)
                for question in random.sample(project_questions, count)
            ]
            session_id = f"sess-{uuid.uuid4().hex[:10]}"

            FALLBACK_EXAM_SESSIONS[session_id] = {
                'session_id': session_id,
                'project_id': project_id,
                'mode': mode,
                'questions': selected_questions,
                'answers': {},
                'started_at': int(time.time()),
            }

            response_questions = []
            for question in selected_questions:
                response_questions.append({
                    'question_id': question['question_id'],
                    'text': question['text'],
                    'answer_options': question['answer_options'],
                    'question_type': question.get('question_type', 'single_choice'),
                    'difficulty': question.get('difficulty', 'medium'),
                    'metadata': question.get('metadata', {}),
                    'time_limit_seconds': 60,
                })

            return {
                'statusCode': 201,
                'headers': cors_headers,
                'body': json.dumps({
                    'session_id': session_id,
                    'questions': response_questions,
                    'mode': mode,
                    'started_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                    'total_time_seconds': len(response_questions) * 60,
                })
            }

        # Protected: POST /api/exams/{session_id}/present
        if method == 'POST' and path.startswith('/api/exams/') and path.endswith('/present'):
            if not _is_authorized(headers):
                return {
                    'statusCode': 401,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'Unauthorized'})
                }

            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({'message': 'presentation recorded'})
            }

        # Protected: POST /api/exams/{session_id}/answers
        if method == 'POST' and path.startswith('/api/exams/') and path.endswith('/answers'):
            if not _is_authorized(headers):
                return {
                    'statusCode': 401,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'Unauthorized'})
                }

            parts = path.strip('/').split('/')
            if len(parts) < 4:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'Invalid session path'})
                }

            session_id = parts[2]
            session = FALLBACK_EXAM_SESSIONS.get(session_id)
            if not session:
                return {
                    'statusCode': 404,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'Session not found'})
                }

            try:
                payload = _parse_json_body(event)
            except Exception:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'Invalid JSON body'})
                }

            question_id = payload.get('question_id')
            if question_id is None:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'question_id is required'})
                }

            question = next((q for q in session['questions'] if q['question_id'] == question_id), None)
            if not question:
                return {
                    'statusCode': 404,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'Question not found in session'})
                }

            evaluation = _evaluate_answer(question, payload)
            session['answers'][question_id] = {
                'answerIndex': evaluation.get('selected_answer', {}).get('index'),
                'selected': evaluation.get('selected_answer'),
                'selectedDisplay': evaluation.get('selected_display'),
                'questionType': evaluation.get('question_type'),
                'isCorrect': evaluation.get('is_correct', False),
                'correctAnswer': evaluation.get('correct_answer'),
                'timeSpent': 0,
                'accepted': evaluation.get('accepted', False),
            }

            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'is_correct': evaluation.get('is_correct', False),
                    'time_spent': 0,
                    'accepted': evaluation.get('accepted', False),
                    'correct_index': question['correct_answer_index'] if session.get('mode') == 'test' else None,
                    'correct_answer': evaluation.get('correct_answer') if session.get('mode') == 'test' else None,
                    'selected_answer': evaluation.get('selected_answer'),
                })
            }

        # Protected: GET /api/exams/{session_id}/review
        if method == 'GET' and path.startswith('/api/exams/') and path.endswith('/review'):
            if not _is_authorized(headers):
                return {
                    'statusCode': 401,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'Unauthorized'})
                }

            parts = path.strip('/').split('/')
            if len(parts) < 4:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'Invalid session path'})
                }

            session_id = parts[2]
            session = FALLBACK_EXAM_SESSIONS.get(session_id)
            if not session:
                return {
                    'statusCode': 404,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'Session not found'})
                }

            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'questions': session['questions'],
                    'answers': session['answers'],
                    'review_time_seconds': len(session['questions']) * 30,
                    'review_started_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                })
            }

        # Protected: POST /api/exams/{session_id}/submit
        if method == 'POST' and path.startswith('/api/exams/') and path.endswith('/submit'):
            if not _is_authorized(headers):
                return {
                    'statusCode': 401,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'Unauthorized'})
                }

            parts = path.strip('/').split('/')
            if len(parts) < 4:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'Invalid session path'})
                }

            session_id = parts[2]
            session = FALLBACK_EXAM_SESSIONS.get(session_id)
            if not session:
                return {
                    'statusCode': 404,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'Session not found'})
                }

            answers = session.get('answers', {})
            total_questions = len(session['questions'])
            correct_count = sum(1 for answer in answers.values() if answer.get('isCorrect'))
            score = (correct_count / total_questions * 100) if total_questions else 0

            result_answers = []
            for question in session['questions']:
                answer_state = answers.get(question['question_id'], {})
                selected_value = answer_state.get('selected')
                if selected_value is None:
                    selected_value = {'index': answer_state.get('answerIndex')}

                result_answers.append({
                    'question_id': question['question_id'],
                    'question_text': question.get('text'),
                    'question_type': question.get('question_type'),
                    'answer_options': question.get('answer_options', []),
                    'selected_answer': selected_value,
                    'selected_display': answer_state.get('selectedDisplay', ''),
                    'correct_answer': answer_state.get('correctAnswer') or _build_correct_answer_payload(question),
                    'is_correct': answer_state.get('isCorrect', False),
                })

            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'attempt_id': f"attempt-{uuid.uuid4().hex[:10]}",
                    'score': round(score, 2),
                    'correct_count': correct_count,
                    'total_questions': total_questions,
                    'answers': result_answers,
                    'completed_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                })
            }

        # Protected: DELETE /api/exams/{session_id}
        if method == 'DELETE' and path.startswith('/api/exams/'):
            if not _is_authorized(headers):
                return {
                    'statusCode': 401,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'Unauthorized'})
                }

            parts = path.strip('/').split('/')
            if len(parts) < 3:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'detail': 'Invalid session path'})
                }

            session_id = parts[2]
            FALLBACK_EXAM_SESSIONS.pop(session_id, None)
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({'message': 'Session cancelled'})
            }
        
        # Not found
        return {
            'statusCode': 404,
            'headers': cors_headers,
            'body': '{"detail":"Not Found"}'
        }

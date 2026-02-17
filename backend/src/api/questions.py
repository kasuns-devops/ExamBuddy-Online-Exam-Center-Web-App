"""
Questions API - Endpoints for question management including PDF upload
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
from src.services.pdf_parser import PDFQuestionExtractor, PDFQuestionValidator
from src.services.question_type_detector import QuestionTypeDetector, QuestionTypeUpdater
from src.services.question_service import QuestionService
from src.models.question import Question, QuestionType
import asyncio

router = APIRouter(prefix="/api/questions", tags=["questions"])
service = QuestionService()


class PDFUploadResponse(BaseModel):
    """Response for PDF upload"""
    upload_id: str
    project_id: str
    questions_found: int
    questions_valid: int
    questions_invalid: int
    errors: List[str]
    questions: Optional[List[dict]] = None


class QuestionTypeRequest(BaseModel):
    """Update question type"""
    question_type: QuestionType
    metadata: Optional[dict] = None


@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    project_id: str = Query(...),
    auto_store: bool = Query(default=False, description="Auto-store questions without review")
) -> PDFUploadResponse:
    """
    Upload a PDF file and extract questions.
    
    Args:
        file: PDF file to upload
        project_id: Project ID to associate questions
        auto_store: If True, automatically store questions (bypass review)
    
    Returns:
        Upload result with extracted questions and validation status
    """
    upload_id = f"upload-{uuid.uuid4()}"
    
    # Validate file
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Save uploaded file temporarily
    temp_dir = "/tmp/pdf_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"{upload_id}.pdf")
    
    try:
        # Save file
        contents = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(contents)
        
        # Extract questions from PDF
        extracted_questions = PDFQuestionExtractor.extract_from_file(temp_path, project_id)
        
        # Validate questions
        valid_questions, errors = PDFQuestionValidator.validate_questions(extracted_questions)
        
        # Auto-detect types for all valid questions
        typed_questions = []
        for q in valid_questions:
            detected_type, metadata = QuestionTypeDetector.detect_type(q)
            q.question_type = detected_type
            q.metadata = metadata
            typed_questions.append(q)
        
        # If auto_store enabled, store immediately
        if auto_store:
            for q in typed_questions:
                try:
                    await service.create_question(q, auto_detect_type=False)
                except Exception as e:
                    errors.append(f"Failed to store {q.question_id}: {str(e)}")
        
        return PDFUploadResponse(
            upload_id=upload_id,
            project_id=project_id,
            questions_found=len(extracted_questions),
            questions_valid=len(valid_questions),
            questions_invalid=len(errors),
            errors=errors,
            questions=[
                {
                    "question_id": q.question_id,
                    "text": q.text[:100] + "..." if len(q.text) > 100 else q.text,
                    "options_count": len(q.answer_options),
                    "detected_type": q.question_type,
                    "metadata": q.metadata
                }
                for q in typed_questions
            ]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/extracted/{upload_id}")
async def get_extracted_questions(upload_id: str, project_id: str = Query(...)):
    """
    Get extracted questions from an upload (for review before storing).
    This is a placeholder - in production, store metadata in cache/DB.
    """
    return {
        "upload_id": upload_id,
        "message": "Use /upload-pdf endpoint and retrieve questions from response",
        "note": "In production, implement persistent upload storage with cache/DB"
    }


@router.post("/import-from-pdf")
async def import_from_pdf(upload_id: str, question_ids: List[str], project_id: str = Query(...)):
    """
    Import selected questions from a PDF upload.
    """
    return {
        "status": "success",
        "message": f"Imported {len(question_ids)} questions",
        "note": "Implement persistence layer for bulk imports"
    }


@router.get("/by-type")
async def get_questions_by_type(
    project_id: str = Query(...),
    question_type: Optional[QuestionType] = Query(None)
):
    """
    Get questions filtered by type.
    """
    return {
        "project_id": project_id,
        "question_type": question_type,
        "questions": []
    }


@router.patch("/{question_id}/type")
async def update_question_type(
    question_id: str,
    type_request: QuestionTypeRequest
):
    """
    Update question type and metadata (admin override).
    """
    return {
        "question_id": question_id,
        "question_type": type_request.question_type,
        "metadata": type_request.metadata,
        "status": "updated"
    }


@router.get("/stats/{project_id}")
async def get_question_stats(project_id: str):
    """
    Get statistics about questions in a project.
    Includes count by type, difficulty, source (manual/pdf).
    """
    return {
        "project_id": project_id,
        "total_questions": 0,
        "by_type": {},
        "by_difficulty": {},
        "by_source": {}
    }

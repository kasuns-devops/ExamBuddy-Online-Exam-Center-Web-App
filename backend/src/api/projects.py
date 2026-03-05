"""
Project API router (admin + student project listing).
"""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from typing import List, Optional

from src.middleware.auth import require_admin_user, require_student_user
from src.services.project_ingestion_service import project_ingestion_service


router = APIRouter(tags=["projects"])


class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)


class StudentProjectItem(BaseModel):
    project_id: str
    name: str
    description: Optional[str]
    question_count: int


@router.post("/v1/admin/projects", status_code=status.HTTP_201_CREATED)
async def create_project(
    request: CreateProjectRequest,
    current_user: dict = Depends(require_admin_user),
):
    return await project_ingestion_service.create_project(
        name=request.name,
        description=request.description,
        admin_id=current_user["user_id"],
    )


@router.post("/v1/admin/projects/{project_id}/documents", status_code=status.HTTP_202_ACCEPTED)
async def upload_project_document(
    project_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(require_admin_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        return await project_ingestion_service.start_document_ingestion(
            project_id=project_id,
            filename=file.filename,
            uploaded_by=current_user["user_id"],
            file_bytes=file_bytes,
            content_type=file.content_type or "application/pdf",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/v1/admin/projects/{project_id}/ingestion")
async def get_project_ingestion_status(
    project_id: str,
    current_user: dict = Depends(require_admin_user),
):
    return await project_ingestion_service.get_ingestion_status(project_id)


@router.get("/v1/student/projects")
async def list_student_projects(
    current_user: dict = Depends(require_student_user),
):
    items = await project_ingestion_service.list_available_projects()
    return {"items": items}

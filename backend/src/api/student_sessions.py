"""
Student sessions API router.
"""
from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.database.dynamodb_client import DynamoDBClient
from src.middleware.auth import require_student_user
from src.services.audit_service import audit_service


router = APIRouter(tags=["student-sessions"])


class StartStudentSessionRequest(BaseModel):
    project_id: str = Field(..., min_length=1)
    mode: str = Field(..., pattern="^(TEST|EXAM)$")


@router.post("/v1/student/sessions", status_code=status.HTTP_201_CREATED)
async def start_student_session(
    request: StartStudentSessionRequest,
    current_user: dict = Depends(require_student_user),
):
    db = DynamoDBClient()
    now = datetime.now(timezone.utc).isoformat()

    session_id = f"session-{uuid.uuid4()}"
    session_item = {
        "PK": f"SESSION#{session_id}",
        "SK": f"SESSION#{session_id}",
        "entity_type": "student_session",
        "session_id": session_id,
        "student_id": current_user["user_id"],
        "project_id": request.project_id,
        "mode": request.mode,
        "status": "STARTED",
        "question_ids": [],
        "started_at": now,
        "updated_at": now,
    }

    try:
        await db.create_student_session(session_item)
        audit_service.log_event(
            event_type="student.session.started",
            actor_id=current_user["user_id"],
            actor_role=current_user.get("role"),
            project_id=request.project_id,
            status="SUCCESS",
            details={"session_id": session_id, "mode": request.mode},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start student session: {exc}",
        )

    return {
        "session_id": session_id,
        "project_id": request.project_id,
        "mode": request.mode,
        "status": "STARTED",
        "question_ids": [],
        "started_at": now,
    }

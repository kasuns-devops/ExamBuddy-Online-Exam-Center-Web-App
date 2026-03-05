"""
Project ingestion orchestration service.
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from src.database.dynamodb_client import DynamoDBClient
from src.database.s3_client import S3Client
from src.models.project import ProjectStatus, ProjectIngestionStatus
from src.services.audit_service import audit_service


class ProjectIngestionService:
    """Shared service for project create/upload/list foundational flows."""

    def __init__(self):
        self.db = DynamoDBClient()
        self.s3 = S3Client()

    async def create_project(self, name: str, admin_id: str, description: Optional[str] = None) -> Dict:
        project_id = f"proj-{uuid.uuid4()}"
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "PK": f"PROJECT#{project_id}",
            "SK": "METADATA",
            "GSI1PK": f"ADMIN#{admin_id}",
            "GSI1SK": f"PROJECT#{now}",
            "GSI2PK": "ALL_PROJECTS",
            "GSI2SK": f"PROJECT#{now}",
            "entity_type": "project",
            "project_id": project_id,
            "name": name,
            "description": description,
            "admin_id": admin_id,
            "archived": False,
            "status": ProjectStatus.DRAFT.value,
            "question_count": 0,
            "created_at": now,
            "updated_at": now,
        }
        await self.db.create_project(item)
        audit_service.log_event(
            event_type="project.created",
            actor_id=admin_id,
            actor_role="admin",
            project_id=project_id,
            status="SUCCESS",
            details={"name": name},
        )
        return item

    async def start_document_ingestion(self, project_id: str, filename: str, uploaded_by: str) -> Dict:
        document_id = f"doc-{uuid.uuid4()}"
        now = datetime.now(timezone.utc).isoformat()
        object_key = self.s3.build_project_document_key(project_id, filename)
        upload = self.s3.generate_project_pdf_upload_url(project_id=project_id, filename=filename)

        document_item = {
            "PK": f"PROJECT#{project_id}",
            "SK": f"DOCUMENT#{document_id}",
            "entity_type": "project_document",
            "document_id": document_id,
            "project_id": project_id,
            "file_name": filename,
            "s3_key": object_key,
            "ingestion_status": ProjectIngestionStatus.UPLOADED.value,
            "uploaded_by": uploaded_by,
            "uploaded_at": now,
            "updated_at": now,
        }
        await self.db.save_project_document(document_item)
        audit_service.log_event(
            event_type="project.document.upload_started",
            actor_id=uploaded_by,
            actor_role="admin",
            project_id=project_id,
            status="SUCCESS",
            details={"document_id": document_id, "file_name": filename},
        )
        return {
            "document_id": document_id,
            "project_id": project_id,
            "status": ProjectIngestionStatus.PROCESSING.value,
            "upload": upload,
            "updated_at": now,
        }

    async def get_ingestion_status(self, project_id: str) -> Dict:
        project = await self.db.get_project(project_id)
        if not project:
            return {
                "project_id": project_id,
                "status": ProjectIngestionStatus.FAILED.value,
                "question_count": 0,
                "error": "Project not found",
            }

        return {
            "project_id": project_id,
            "status": project.get("status", ProjectStatus.DRAFT.value),
            "question_count": project.get("question_count", 0),
            "error": None,
            "updated_at": project.get("updated_at"),
        }

    async def list_available_projects(self) -> List[Dict]:
        projects = await self.db.list_projects(limit=100)
        return [
            {
                "project_id": item.get("project_id"),
                "name": item.get("name"),
                "description": item.get("description"),
                "question_count": item.get("question_count", 0),
            }
            for item in projects
            if item.get("status") == ProjectStatus.PUBLISHED.value
            and not item.get("archived", False)
            and item.get("question_count", 0) > 0
        ]


project_ingestion_service = ProjectIngestionService()

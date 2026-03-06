"""
Project ingestion orchestration service.
"""
import os
import tempfile
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from src.config import settings
from src.database.dynamodb_client import DynamoDBClient
from src.database.s3_client import S3Client
from src.models.project import (
    ProjectStatus,
    ProjectIngestionStatus,
    Project,
    ProjectDocument,
    map_ingestion_to_project_status,
)
from src.services.audit_service import audit_service
from src.services.pdf_parser import PDFQuestionExtractor, PDFQuestionValidator, PDFQuestionNormalizer


class ProjectIngestionService:
    """Shared service for project create/upload/list foundational flows."""

    def __init__(self):
        self.db = DynamoDBClient()
        self.s3 = S3Client()

    async def _update_project_status(
        self,
        project_id: str,
        next_status: ProjectStatus,
        question_count: Optional[int] = None,
    ) -> None:
        project = await self.db.get_project(project_id)
        if not project:
            raise ValueError("Project not found")

        current_status = ProjectStatus(project.get("status", ProjectStatus.DRAFT.value))
        if not Project.can_transition(current_status, next_status):
            raise ValueError(f"Invalid project status transition: {current_status.value} -> {next_status.value}")

        expression = "SET #status = :status, updated_at = :updated_at"
        values = {
            ":status": next_status.value,
            ":updated_at": datetime.now(timezone.utc).isoformat(),
        }
        names = {"#status": "status"}

        if question_count is not None:
            expression += ", question_count = :question_count"
            values[":question_count"] = int(question_count)

        await self.db.update_item(
            pk=f"PROJECT#{project_id}",
            sk="METADATA",
            update_expression=expression,
            expression_attribute_values=values,
            expression_attribute_names=names,
        )

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

    async def start_document_ingestion(
        self,
        project_id: str,
        filename: str,
        uploaded_by: str,
        file_bytes: bytes,
        content_type: str,
    ) -> Dict:
        project = await self.db.get_project(project_id)
        if not project:
            raise ValueError("Project not found")

        max_size_bytes = settings.pdf_ingestion_max_file_size_mb * 1024 * 1024
        if len(file_bytes) > max_size_bytes:
            raise ValueError(f"PDF exceeds maximum size of {settings.pdf_ingestion_max_file_size_mb}MB")

        allowed_types = [mime.strip().lower() for mime in settings.pdf_ingestion_allowed_mime_types]
        normalized_content_type = (content_type or "").split(";")[0].strip().lower()
        if normalized_content_type not in allowed_types:
            raise ValueError("Unsupported file type; only PDF uploads are allowed")

        if not filename.lower().endswith('.pdf'):
            raise ValueError("Unsupported file extension; expected .pdf")

        document_id = f"doc-{uuid.uuid4()}"
        now = datetime.now(timezone.utc).isoformat()
        object_key = self.s3.build_project_document_key(project_id, filename)

        document = ProjectDocument(
            document_id=document_id,
            project_id=project_id,
            file_name=filename,
            s3_key=object_key,
            content_type=normalized_content_type,
            file_size_bytes=len(file_bytes),
            ingestion_status=ProjectIngestionStatus.PROCESSING,
            uploaded_by=uploaded_by,
            uploaded_at=now,
            updated_at=now,
        )

        await self.db.save_project_document(document.to_dynamodb_item())
        await self._update_project_status(
            project_id,
            map_ingestion_to_project_status(ProjectIngestionStatus.PROCESSING),
        )

        temp_path = None
        try:
            await self.s3.upload_file(
                file_data=file_bytes,
                object_key=object_key,
                bucket_name=settings.s3_project_documents_bucket,
                content_type=normalized_content_type,
            )

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.write(file_bytes)
            temp_file.flush()
            temp_file.close()
            temp_path = temp_file.name

            extracted_questions = PDFQuestionExtractor.extract_from_file(temp_path, project_id)
            valid_questions, validation_errors = PDFQuestionValidator.validate_questions(extracted_questions)
            normalized_questions, normalization_warnings = PDFQuestionNormalizer.normalize_questions(valid_questions)

            if not normalized_questions:
                raise ValueError("PDF parsing produced no valid question-answer pairs")

            question_items = []
            for question in normalized_questions:
                question_items.append(
                    {
                        "PK": f"PROJECT#{project_id}",
                        "SK": f"QUESTION#{question.question_id}",
                        "GSI1PK": f"QUESTION#{question.question_id}",
                        "GSI1SK": f"PROJECT#{project_id}",
                        **question.dict(),
                    }
                )

            await self.db.save_question_items(question_items)
            await self._update_project_status(project_id, ProjectStatus.PUBLISHED, question_count=len(question_items))

            await self.db.update_item(
                pk=f"PROJECT#{project_id}",
                sk=f"DOCUMENT#{document_id}",
                update_expression="SET ingestion_status = :status, processed_at = :processed_at, updated_at = :updated_at",
                expression_attribute_values={
                    ":status": ProjectIngestionStatus.COMPLETED.value,
                    ":processed_at": datetime.now(timezone.utc).isoformat(),
                    ":updated_at": datetime.now(timezone.utc).isoformat(),
                },
            )

            audit_service.log_event(
                event_type="project.document.ingested",
                actor_id=uploaded_by,
                actor_role="admin",
                project_id=project_id,
                status="SUCCESS",
                details={
                    "document_id": document_id,
                    "question_count": len(question_items),
                    "validation_errors": validation_errors,
                    "normalization_warnings": normalization_warnings,
                },
            )

            return {
                "document_id": document_id,
                "project_id": project_id,
                "status": ProjectStatus.PUBLISHED.value,
                "question_count": len(question_items),
                "errors": validation_errors + normalization_warnings,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            await self._update_project_status(project_id, ProjectStatus.FAILED, question_count=0)
            await self.db.update_item(
                pk=f"PROJECT#{project_id}",
                sk=f"DOCUMENT#{document_id}",
                update_expression="SET ingestion_status = :status, error_message = :error_message, updated_at = :updated_at",
                expression_attribute_values={
                    ":status": ProjectIngestionStatus.FAILED.value,
                    ":error_message": str(exc),
                    ":updated_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            audit_service.log_event(
                event_type="project.document.ingested",
                actor_id=uploaded_by,
                actor_role="admin",
                project_id=project_id,
                status="FAILED",
                details={"document_id": document_id, "error": str(exc)},
            )
            raise
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

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
                "title": item.get("name"),
                "name": item.get("name"),
                "description": item.get("description"),
                "question_count": item.get("question_count", 0),
            }
            for item in projects
            if item.get("status") == ProjectStatus.PUBLISHED.value
            and not item.get("archived", False)
            and item.get("is_active", True)
            and item.get("question_count", 0) > 0
        ]


project_ingestion_service = ProjectIngestionService()

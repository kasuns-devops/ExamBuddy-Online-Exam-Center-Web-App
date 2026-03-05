"""
Audit service for structured project/session event logging.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class AuditService:
    """Simple structured audit logger."""

    @staticmethod
    def log_event(
        event_type: str,
        actor_id: Optional[str] = None,
        actor_role: Optional[str] = None,
        project_id: Optional[str] = None,
        status: str = "INFO",
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "status": status,
            "actor_id": actor_id,
            "actor_role": actor_role,
            "project_id": project_id,
            "details": details or {},
        }
        print(f"AUDIT_EVENT {payload}")
        return payload


audit_service = AuditService()

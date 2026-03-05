"""
Shared authentication and RBAC helpers.
"""
from typing import Dict

from fastapi import Depends, HTTPException, status

from src.middleware.auth_middleware import get_current_user


ROLE_ADMIN = "admin"
ROLE_STUDENT = "candidate"
ROLE_STUDENT_ALIASES = {"student", "candidate"}


def _normalize_role(user_role: str) -> str:
    return (user_role or "").strip().lower()


def require_roles(*allowed_roles: str):
    """Return dependency that enforces one of the allowed roles."""
    normalized_allowed = {
        _normalize_role(role)
        for role in allowed_roles
        if isinstance(role, str) and role.strip()
    }

    async def _role_guard(current_user: Dict = Depends(get_current_user)) -> Dict:
        role = _normalize_role(current_user.get("role", ""))
        if role not in normalized_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role permissions"
            )
        return current_user

    return _role_guard


async def require_admin_user(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Require admin role."""
    return await require_roles(ROLE_ADMIN)(current_user)


async def require_student_user(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Require student/candidate role."""
    return await require_roles(*ROLE_STUDENT_ALIASES)(current_user)

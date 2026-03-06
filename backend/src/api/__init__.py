# API Endpoints Package

from .projects import router as projects_router
from .exams import router as exams_router
from .exams import student_sessions_router


def register_api_routers(app):
	"""Register API routers for project ingestion and exam/session flows."""
	app.include_router(projects_router)
	app.include_router(exams_router)
	app.include_router(student_sessions_router)

__all__ = [
	"projects_router",
	"exams_router",
	"student_sessions_router",
	"register_api_routers",
]

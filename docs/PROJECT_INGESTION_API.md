# Project Ingestion API

## Overview
This document describes the project ingestion and student project selection/session APIs introduced for feature `001-project-pdf-ingestion`.

## Admin Endpoints
- `POST /v1/admin/projects`
  - Creates a project in `DRAFT` status.
  - Request body: `{ "name": string, "description"?: string }`
- `POST /v1/admin/projects/{project_id}/documents`
  - Uploads a PDF for ingestion (`multipart/form-data`, field: `file`).
  - Triggers parse/normalize/persist flow and updates project status to `PUBLISHED` or `FAILED`.
- `GET /v1/admin/projects/{project_id}/ingestion`
  - Returns ingestion and project status with question count.

## Student Endpoints
- `GET /v1/student/projects`
  - Returns only selectable projects: `PUBLISHED`, active, non-archived, and `question_count > 0`.
- `POST /v1/student/sessions`
  - Starts a project-pinned session for `TEST` or `EXAM` mode.
  - Detects conflicts when an active session already exists for the same student/project.

## Security
- Admin endpoints require admin role.
- Student endpoints require candidate/student role.

## Notes
- Status transitions are enforced in project model lifecycle logic.
- Session scoring is constrained to questions belonging to the selected project.
- Canonical contract source: `specs/001-project-pdf-ingestion/contracts/openapi.yaml`.

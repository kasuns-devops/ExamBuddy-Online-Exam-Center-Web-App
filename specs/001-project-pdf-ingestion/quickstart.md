# Quickstart: Project PDF Question Ingestion

## Prerequisites
- AWS-backed dev environment configured for backend and frontend.
- Valid Cognito users for `admin` and `student` roles.
- Existing API + frontend running locally or deployed.

## 1) Backend setup
1. Configure backend env for:
   - DynamoDB table access for projects/questions/sessions.
   - S3 bucket for uploaded PDFs.
   - Max PDF size and accepted content type settings.
2. Install dependencies (if newly introduced): `pdfplumber`, `pypdf`.
3. Start backend locally via existing run path (SAM/local FastAPI flow used in repo).

## 2) Admin flow validation
1. Authenticate as admin.
2. Create project using `POST /v1/admin/projects`.
3. Upload PDF via `POST /v1/admin/projects/{projectId}/documents` (multipart form-data).
4. Poll `GET /v1/admin/projects/{projectId}/ingestion` until `PUBLISHED` or `FAILED`.
5. Verify parsed question count > 0 and error handling for invalid PDFs.

## 3) Student flow validation
1. Authenticate as student.
2. List selectable projects via `GET /v1/student/projects`.
3. Start a test session via `POST /v1/student/sessions` with `mode=TEST`.
4. Start an exam session via `POST /v1/student/sessions` with `mode=EXAM`.
5. Confirm all returned questions belong to selected `project_id` and scoring aligns with stored answer keys.

## 4) Contract verification
- Validate requests/responses against [contracts/openapi.yaml](./contracts/openapi.yaml).
- Confirm authorization: admin endpoints reject student tokens; student endpoints reject unauthenticated users.

## 5) Performance spot checks
- Measure parse latency for representative 50-question PDF (<3s target).
- Measure session start p95 latency (<1s target) and submit p95 latency (<500ms target).

## Rollback / Recovery
- If ingestion fails, project remains non-published (`FAILED`) and hidden from student listing.
- Admin can re-upload a corrected PDF to retry processing.

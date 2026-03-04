# Implementation Plan: Project PDF Question Ingestion

**Branch**: `001-project-pdf-ingestion` | **Date**: 2026-03-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-project-pdf-ingestion/spec.md`

## Summary

Implement an admin-driven project ingestion flow where admins create projects and upload PDF question banks, parse and persist questions/answer keys, and expose project-aware student exam start flows using the existing FastAPI + AWS serverless backend and React frontend.

## Technical Context

**Language/Version**: Python 3.11 (backend), JavaScript ES modules + React 19 (frontend)  
**Primary Dependencies**: FastAPI, Mangum, boto3, pdfplumber, pypdf, React, React Router, Zustand, Axios  
**Storage**: DynamoDB for project/question metadata, S3 for uploaded PDF source files and artifacts  
**Testing**: pytest (+ integration/contract style API tests), frontend build verification via Vite  
**Target Platform**: AWS Lambda + API Gateway backend, CloudFront/S3 hosted web frontend
**Project Type**: Web application (frontend + backend)  
**Performance Goals**: PDF parsing <3s for ~50 Q/A pairs, project-backed exam start <1s, answer submit <500ms  
**Constraints**: Stateless Lambda execution, role-based access control, mobile-first UI behavior, no direct frontend DB access  
**Scale/Scope**: Support at least 100 concurrent active exams, multi-project question banks, admin and student roles

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Mobile-First Responsiveness**: Student project-selection and exam-start UX remain mobile-first; admin upload flow will include touch-safe controls and responsive forms.
- [x] **API-First Architecture**: Project creation, PDF upload, ingestion status, project listing, and session start are exposed via REST endpoints with contract docs.
- [x] **Serverless-Ready**: Design remains stateless with S3/DynamoDB persistence; parsing pipeline modeled for Lambda execution constraints.
- [x] **Secure by Default**: Admin-only upload/create endpoints enforced by role; student endpoints filtered by project availability; input/file validation required.
- [x] **Performance Targets**: Parsing and session-start performance targets explicitly captured and tested with representative payloads.

**Violations Requiring Justification**: N/A

## Project Structure

### Documentation (this feature)

```text
specs/001-project-pdf-ingestion/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   ├── models/
│   ├── services/
│   └── database/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── stores/
└── (vite build/test tooling)

infrastructure/
└── deployment/config assets
```

**Structure Decision**: Use the existing web application split (`backend/` + `frontend/`) and extend current API/service layers rather than introducing new top-level services.

## Phase 0 Research Focus

1. PDF parsing strategy and normalization rules for stable question/answer extraction.
2. Project publication lifecycle and ingest failure semantics.
3. DynamoDB + S3 modeling pattern for project-scoped question banks in serverless flows.

## Phase 1 Design Outputs

- Data model for `Project`, `ProjectDocument`, `QuestionItem`, `AnswerKey`, and `StudentSession` linkage.
- REST contracts for admin ingest and student project selection/session start.
- Quickstart covering secrets, deploy flow, and end-to-end verification.

## Post-Design Constitution Re-check

- [x] Mobile-first behavior preserved for student flows and new admin forms.
- [x] API-first contract artifacts generated for all new backend capabilities.
- [x] Serverless-compatible persistence and stateless ingestion/session behavior confirmed.
- [x] RBAC and validation boundaries present in design artifacts.
- [x] Performance objectives and measurable acceptance checks mapped to design.

## Complexity Tracking

No constitution violations or exceptional complexity decisions identified at planning stage.

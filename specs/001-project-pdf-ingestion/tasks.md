# Tasks: Project PDF Question Ingestion

**Input**: Design documents from `/specs/001-project-pdf-ingestion/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/openapi.yaml`, `quickstart.md`

**Tests**: Test tasks are not included because the specification does not explicitly require a TDD-first or test-creation workflow.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare dependencies and config for project-based PDF ingestion.

- [x] T001 Add PDF parsing dependencies (`pdfplumber`, `pypdf`) in `backend/requirements.txt`
- [x] T002 Add ingestion environment settings (max file size, accepted MIME, bucket/table names) in `backend/src/config.py`
- [x] T003 [P] Add project-ingestion constants and status enums in `backend/src/models/project.py`
- [x] T004 [P] Add frontend API route constants for project ingestion endpoints in `frontend/src/services/api.js`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared backend/frontend foundations required by all user stories.

**⚠️ CRITICAL**: No user story work starts until this phase is complete.

- [x] T005 Create DynamoDB access helpers for project/question/session records in `backend/src/database/dynamodb_client.py`
- [x] T006 [P] Create S3 upload/download helpers for project PDFs in `backend/src/database/s3_client.py`
- [x] T007 Implement shared RBAC guard utilities for admin/student endpoint protection in `backend/src/middleware/auth.py`
- [x] T008 [P] Implement structured audit logging helper for project/session events in `backend/src/services/audit_service.py`
- [x] T009 Create project ingestion orchestration service interface in `backend/src/services/project_ingestion_service.py`
- [x] T010 Wire new API routers for projects and student sessions in `backend/src/main.py`

**Checkpoint**: Foundation complete; user stories can proceed.

---

## Phase 3: User Story 1 - Admin uploads project question set (Priority: P1) 🎯 MVP

**Goal**: Allow admins to create a project, upload PDF, parse Q/A pairs, and publish only valid banks.

**Independent Test**: Admin creates project, uploads valid PDF, and sees persisted questions/answers; invalid PDF returns clear failure without publishing.

### Implementation for User Story 1

- [x] T011 [US1] Implement `Project` validation/state transition rules in `backend/src/models/project.py`
- [x] T012 [P] [US1] Implement `ProjectDocument` ingestion model and status mapping in `backend/src/models/project.py`
- [x] T013 [P] [US1] Implement parser normalization utilities for duplicate/empty question handling in `backend/src/services/pdf_parser.py`
- [x] T014 [US1] Implement ingestion pipeline (`upload -> parse -> persist -> publish/fail`) in `backend/src/services/project_ingestion_service.py`
- [x] T015 [US1] Implement admin endpoint `POST /v1/admin/projects` in `backend/src/api/projects.py`
- [x] T016 [US1] Implement admin endpoint `POST /v1/admin/projects/{projectId}/documents` in `backend/src/api/projects.py`
- [x] T017 [US1] Implement admin endpoint `GET /v1/admin/projects/{projectId}/ingestion` in `backend/src/api/projects.py`
- [x] T018 [US1] Register project API router and auth requirements in `backend/src/api/__init__.py`
- [x] T019 [US1] Create admin upload UI and form validation in `frontend/src/components/admin/ProjectUploadForm.jsx`
- [x] T020 [US1] Add admin upload page styling and mobile-safe layout in `frontend/src/components/admin/ProjectUploadForm.css`
- [x] T021 [US1] Add admin project ingestion client methods in `frontend/src/services/examService.js`

**Checkpoint**: US1 is independently functional and publish-safe.

---

## Phase 4: User Story 2 - Student selects an available project (Priority: P2)

**Goal**: Show students only selectable published projects and support clear empty/error states.

**Independent Test**: Student opens selection page and sees only active published projects; empty-state appears when none are available.

### Implementation for User Story 2

- [x] T022 [US2] Implement student visibility filtering (`PUBLISHED` + active + questionCount>0) in `backend/src/services/project_ingestion_service.py`
- [x] T023 [US2] Implement endpoint `GET /v1/student/projects` in `backend/src/api/projects.py`
- [x] T024 [P] [US2] Add student project-list API client and response mapping in `frontend/src/services/examService.js`
- [x] T025 [US2] Update project selection data flow/state handling in `frontend/src/components/candidate/ProjectSelection.jsx`
- [x] T026 [US2] Add empty-state and loading/error visuals for project selection in `frontend/src/components/candidate/ProjectSelection.css`
- [x] T027 [US2] Persist selected project context for exam start in `frontend/src/stores/examStore.js`

**Checkpoint**: US2 independently lists and selects valid projects only.

---

## Phase 5: User Story 3 - Student starts test or exam from selected project (Priority: P3)

**Goal**: Start test/exam sessions pinned to selected project and score against stored answer keys.

**Independent Test**: Student starts both TEST and EXAM from one project; delivered questions/scoring reference only that project data.

### Implementation for User Story 3

- [ ] T028 [US3] Implement `StudentSession` project-pinning and conflict rules in `backend/src/models/attempt.py`
- [ ] T029 [P] [US3] Implement session question loading constrained by `project_id` in `backend/src/services/question_service.py`
- [ ] T030 [US3] Implement session start endpoint `POST /v1/student/sessions` in `backend/src/api/exams.py`
- [ ] T031 [US3] Enforce project-scoped answer-key evaluation during scoring in `backend/src/services/exam_service.py`
- [ ] T032 [P] [US3] Add session start API call (`mode=TEST|EXAM`) in `frontend/src/services/examService.js`
- [ ] T033 [US3] Pass selected project ID into exam start flow in `frontend/src/pages/ExamPage.jsx`
- [ ] T034 [US3] Add session-start validation and blocking messages in `frontend/src/pages/ExamPage.css`

**Checkpoint**: US3 independently starts/scopes sessions and scoring by selected project.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete documentation, consistency, and end-to-end readiness across all stories.

- [ ] T035 [P] Update API documentation for new project/session endpoints in `docs/`
- [ ] T036 Add quickstart verification notes/results in `specs/001-project-pdf-ingestion/quickstart.md`
- [ ] T037 [P] Align OpenAPI contract details with implemented request/response payloads in `specs/001-project-pdf-ingestion/contracts/openapi.yaml`
- [ ] T038 Run end-to-end manual validation and capture findings in `specs/001-project-pdf-ingestion/research.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Starts immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1 completion and blocks all user stories.
- **Phase 3 (US1)**: Starts after Phase 2; establishes admin ingest MVP.
- **Phase 4 (US2)**: Starts after Phase 2; depends on published projects from US1 for meaningful validation.
- **Phase 5 (US3)**: Starts after Phase 2; functionally depends on US1 project banks and uses US2 selection context.
- **Phase 6 (Polish)**: Starts after all targeted stories complete.

### User Story Dependency Graph

- **US1 (P1)** → enables **US2 (P2)** and **US3 (P3)**
- **US2 (P2)** → provides selected project context consumed by **US3 (P3)**
- **US3 (P3)** → final student outcome on top of US1+US2

---

## Parallel Execution Examples

### User Story 1

- Parallelizable tasks: `T012`, `T013` after `T011`; frontend tasks `T019` and `T020` can run in parallel once `T021` contract is agreed.

### User Story 2

- Parallelizable tasks: `T024` can run in parallel with backend `T022`/`T023`; UI styling `T026` can run in parallel with `T025`.

### User Story 3

- Parallelizable tasks: backend loader `T029` and frontend API client `T032` can run in parallel; `T033` and `T034` can run in parallel after API shape is stable.

---

## Implementation Strategy

### MVP First (US1)

1. Complete Phases 1 and 2.
2. Deliver Phase 3 (US1) end-to-end.
3. Validate admin upload and publish/fail behavior before expanding scope.

### Incremental Delivery

1. Ship US1 (admin ingestion and publish safety).
2. Ship US2 (student project discovery and selection).
3. Ship US3 (project-scoped test/exam starts and scoring).
4. Finish with Phase 6 polish and docs alignment.

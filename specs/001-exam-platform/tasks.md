# Tasks: ExamBuddy Online Exam Center Platform

**Feature Branch**: `001-exam-platform`  
**Input**: Design documents from `/specs/001-exam-platform/`  
**Prerequisites**: [plan.md](plan.md) (architecture), [spec.md](spec.md) (user stories), [research.md](research.md) (technical decisions)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **Checkbox**: Always `- [ ]` (markdown task checkbox)
- **[P]**: Parallelizable task (different files, no dependencies on incomplete tasks)
- **[Story]**: User story label (US1, US2, US3, US4, US5) - required for user story phases only
- **File paths**: Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- **Infrastructure**: `backend/template.yaml`, `docker-compose.yml`, `frontend/Dockerfile`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize backend directory with Python 3.11 project structure at backend/
- [x] T002 Create backend/requirements.txt with FastAPI, boto3, pydantic, python-jose, passlib, pytest dependencies
- [x] T003 [P] Initialize frontend directory with React 18 project at frontend/ using create-react-app or Vite
- [x] T004 [P] Create backend/Dockerfile for local development with Python 3.11 base image
- [x] T005 [P] Create frontend/Dockerfile for local development with Node.js 18 base image
- [x] T006 Create docker-compose.yml at repository root with services: backend, frontend, dynamodb-local, localstack-s3
- [x] T007 [P] Create backend/template.yaml (AWS SAM) with Lambda function definitions and API Gateway REST API
- [x] T008 [P] Create .env.example files for backend and frontend with required environment variables
- [x] T009 [P] Create backend/src/config.py to load environment variables (S3 bucket names, DynamoDB table names, Cognito config)
- [x] T010 [P] Create backend/README.md with local dev setup instructions (docker-compose up, SAM local testing)
- [x] T011 [P] Create frontend/README.md with setup instructions (npm install, npm start, environment variables)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T012 Create AWS Cognito User Pool via AWS Console or CloudFormation with email/password auth and custom 'role' attribute
- [ ] T013 Create DynamoDB table 'exambuddy-main' with PK (string), SK (string), and 3 GSIs per data-model.md schema
- [ ] T014 [P] Create S3 bucket 'exambuddy-pdfs' with versioning enabled and lifecycle policy for 90-day retention
- [ ] T015 [P] Create S3 bucket 'exambuddy-exports' for CSV/PDF result downloads with 7-day expiration
- [ ] T016 [P] Configure S3 bucket CORS policy on exambuddy-pdfs to allow presigned URL uploads from frontend origin
- [x] T017 Create backend/src/database/dynamodb_client.py with boto3 DynamoDB client initialization and query helpers
- [x] T018 [P] Create backend/src/database/s3_client.py with boto3 S3 client and presigned URL generation methods
- [x] T019 Create backend/src/models/user.py with User Pydantic model (user_id, email, password_hash, role enum)
- [x] T020 [P] Create backend/src/models/project.py with Project Pydantic model (project_id, name, description, admin_id, archived)
- [x] T021 [P] Create backend/src/models/question.py with Question Pydantic model (question_id, project_id, text, answer_options, correct_index)
- [x] T022 [P] Create backend/src/models/attempt.py with Attempt Pydantic model (attempt_id, candidate_id, project_id, mode, difficulty, score)
- [x] T023 Create backend/src/middleware/auth_middleware.py to verify Cognito JWT tokens using JWKS endpoint
- [x] T024 [P] Create backend/src/middleware/error_handler.py for global exception handling with structured error responses
- [x] T025 Create backend/src/main.py to initialize FastAPI app, register middleware, include API routers, and Mangum handler
- [x] T026 Create frontend/src/services/api.js with Axios instance including auth interceptor to attach JWT tokens to requests
- [x] T027 [P] Create frontend/src/hooks/useAuth.js for authentication state management (login, logout, token refresh, user role)
- [x] T028 [P] Create frontend/src/components/layout/Header.jsx with navigation, logout button, and role-based menu items
- [x] T029 [P] Create frontend/src/App.jsx with React Router routes for LoginPage, DashboardPage, ExamPage, ResultPage
- [x] T030 [P] Create frontend/src/styles/global.css with mobile-first responsive breakpoints (320px, 768px, 1024px)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Candidate Takes Timed Exam (Priority: P1) 🎯 MVP

**Goal**: Deliver functional online exam flow with random question selection, per-question timers, review phase, and scoring

**Independent Test**: Pre-load question bank, candidate completes exam session, verify score calculation and result display

### Implementation for User Story 1

- [ ] T031 [P] [US1] Create backend/src/services/question_service.py with random_select_questions(project_id, count) method
- [ ] T032 [P] [US1] Create backend/src/services/exam_service.py with start_exam_session, validate_answer, calculate_score methods
- [ ] T033 [P] [US1] Create backend/src/api/exams.py with POST /exams/start endpoint (random question selection, create session)
- [ ] T034 [US1] Create backend/src/api/exams.py POST /exams/{session_id}/answers endpoint with server-side timer validation
- [ ] T035 [US1] Create backend/src/api/exams.py GET /exams/{session_id}/review endpoint to fetch review phase data (Exam mode)
- [ ] T036 [US1] Create backend/src/api/exams.py POST /exams/{session_id}/submit endpoint to finalize exam and persist attempt
- [ ] T037 [US1] Create backend/src/api/exams.py DELETE /exams/{session_id} endpoint to cancel exam (discard attempt)
- [ ] T038 [P] [US1] Create frontend/src/stores/examStore.js Zustand store with exam state (questions, answers, currentIndex, timer)
- [ ] T039 [P] [US1] Create frontend/src/hooks/useExamTimer.js custom hook with Date.now() recalculation and auto-advance callback
- [ ] T040 [P] [US1] Create frontend/src/components/candidate/ProjectSelection.jsx to list active projects for exam start
- [ ] T041 [P] [US1] Create frontend/src/components/candidate/ExamConfig.jsx form (mode, difficulty, question count selection)
- [ ] T042 [US1] Create frontend/src/components/candidate/QuestionCard.jsx to display question text and answer options
- [ ] T043 [US1] Create frontend/src/components/shared/Timer.jsx countdown timer component with formatted time display
- [ ] T044 [US1] Create frontend/src/components/candidate/ExamControls.jsx with Next, Submit, Cancel buttons and disabled states
- [ ] T045 [US1] Create frontend/src/components/shared/ProgressBar.jsx showing question X of Y completion indicator
- [ ] T046 [US1] Create frontend/src/components/candidate/ReviewPhase.jsx for Exam mode review (read-only questions, half-time)
- [ ] T047 [US1] Create frontend/src/components/candidate/ResultSummary.jsx displaying score, correctness, time per question
- [ ] T048 [US1] Create frontend/src/pages/ExamPage.jsx to orchestrate exam flow (config → questions → review → results)
- [ ] T049 [US1] Create frontend/src/services/examService.js with API calls: startExam, submitAnswer, getReview, finalizeExam, cancelExam
- [ ] T050 [US1] Implement answer validation logic in backend/src/services/exam_service.py to check correctness and record time spent
- [ ] T051 [US1] Implement scoring algorithm in backend/src/services/exam_service.py: (correct_count / total_questions) × 100
- [ ] T052 [US1] Add server-side timer validation in backend/src/api/exams.py to reject answers submitted after time limit + 2s grace period
- [ ] T053 [US1] Implement session state persistence in DynamoDB to track active exam sessions (for recovery on disconnection)
- [ ] T054 [US1] Add error handling in frontend/src/pages/ExamPage.jsx for network failures, timer expiration, invalid submissions

**Checkpoint**: User Story 1 complete - candidates can take timed exams end-to-end

---

## Phase 4: User Story 2 - Admin Manages Question Bank (Priority: P2) 🎯 MVP

**Goal**: Enable admins to create projects, upload PDF questions, manually enter questions, and manage question bank

**Independent Test**: Admin uploads 50-question PDF, verifies duplicate detection, manually adds questions, confirms retrieval

### Implementation for User Story 2

- [ ] T055 [P] [US2] Create backend/src/services/pdf_service.py with extract_qa_pairs(pdf_bytes) using pypdf + pdfplumber fallback
- [ ] T056 [P] [US2] Create backend/src/services/question_service.py detect_duplicates(questions) method using text normalization
- [ ] T057 [P] [US2] Create backend/src/api/projects.py with GET /projects endpoint (list all, filter by archived status)
- [ ] T058 [US2] Create backend/src/api/projects.py POST /projects endpoint to create new project (admin-only, RBAC check)
- [ ] T059 [US2] Create backend/src/api/projects.py GET /projects/{id} endpoint to fetch project details with question count
- [ ] T060 [US2] Create backend/src/api/projects.py PUT /projects/{id} endpoint to update project name/description (admin-only)
- [ ] T061 [US2] Create backend/src/api/projects.py DELETE /projects/{id} endpoint with check for active exam sessions before deletion
- [ ] T062 [P] [US2] Create backend/src/api/questions.py GET /projects/{id}/questions endpoint to list all questions in project
- [ ] T063 [US2] Create backend/src/api/questions.py POST /projects/{id}/questions endpoint for manual question entry (admin-only)
- [ ] T064 [US2] Create backend/src/api/questions.py POST /projects/{id}/questions/upload-url endpoint to generate S3 presigned POST URL
- [ ] T065 [US2] Create backend/src/api/questions.py PUT /questions/{id} endpoint to update question text/answers (admin-only)
- [ ] T066 [US2] Create backend/src/api/questions.py DELETE /questions/{id} endpoint with confirmation warning (admin-only)
- [ ] T067 [US2] Create Lambda function backend/src/lambda/pdf_parser.py triggered by S3 ObjectCreated event to parse uploaded PDFs
- [ ] T068 [US2] Implement PDF validation in backend/src/services/pdf_service.py: magic bytes check, file size <10MB, text extraction
- [ ] T069 [US2] Implement Q&A structure detection in backend/src/services/pdf_service.py to identify question text and [A]/[B]/[C] answer options
- [ ] T070 [US2] Add duplicate detection in backend/src/lambda/pdf_parser.py to compare uploaded questions against existing project questions
- [ ] T071 [US2] Store parsing status in DynamoDB (parsing/completed/failed) for frontend polling in backend/src/lambda/pdf_parser.py
- [ ] T072 [P] [US2] Create frontend/src/components/admin/ProjectList.jsx to display projects with question counts and action buttons
- [ ] T073 [P] [US2] Create frontend/src/components/admin/ProjectForm.jsx modal for create/edit project with name and description fields
- [ ] T074 [P] [US2] Create frontend/src/components/admin/QuestionList.jsx table showing questions with edit/delete actions
- [ ] T075 [P] [US2] Create frontend/src/components/admin/QuestionForm.jsx modal for manual question entry with 2-6 answer options
- [ ] T076 [P] [US2] Create frontend/src/components/admin/PDFUpload.jsx with file input, upload progress, and parsing status polling
- [ ] T077 [US2] Create frontend/src/components/admin/AdminDashboard.jsx main view with project list and navigation
- [ ] T078 [US2] Create frontend/src/services/projectService.js with API calls: listProjects, createProject, updateProject, deleteProject
- [ ] T079 [US2] Create frontend/src/services/questionService.js with API calls: listQuestions, createQuestion, updateQuestion, deleteQuestion, uploadPDF
- [ ] T080 [US2] Implement S3 direct upload in frontend/src/services/questionService.js using presigned POST URL with FormData
- [ ] T081 [US2] Implement parsing status polling in frontend/src/components/admin/PDFUpload.jsx (poll every 2 sec for 60 sec timeout)
- [ ] T082 [US2] Add form validation in frontend/src/components/admin/QuestionForm.jsx: min 2 answers, max 6 answers, exactly 1 correct
- [ ] T083 [US2] Add confirmation dialogs in frontend/src/components/admin/QuestionList.jsx for delete actions with warning text
- [ ] T084 [US2] Implement error display in frontend/src/components/admin/PDFUpload.jsx for parsing failures with actionable messages

**Checkpoint**: User Story 2 complete - admins can manage complete question bank lifecycle

---

## Phase 5: User Story 3 - Candidate Takes Practice Test (Priority: P3)

**Goal**: Implement Test mode with immediate correct answer feedback after each question

**Independent Test**: Candidate selects Test mode, answers questions with immediate feedback, completes without review phase

### Implementation for User Story 3

- [ ] T085 [P] [US3] Update backend/src/services/exam_service.py to support mode='Test' with immediate correctness flag in response
- [ ] T086 [US3] Modify backend/src/api/exams.py POST /exams/{session_id}/answers to return correct_answer_index for Test mode
- [ ] T087 [US3] Update frontend/src/stores/examStore.js to track revealed answers in Test mode
- [ ] T088 [US3] Modify frontend/src/components/candidate/QuestionCard.jsx to highlight correct answer green immediately in Test mode
- [ ] T089 [US3] Update frontend/src/components/candidate/ExamControls.jsx to show only Next button in Test mode (no Submit/review)
- [ ] T090 [US3] Modify frontend/src/pages/ExamPage.jsx to skip review phase entirely for Test mode (direct to results)
- [ ] T091 [US3] Add visual differentiation in frontend/src/components/candidate/QuestionCard.jsx for selected answer (red if wrong)

**Checkpoint**: User Story 3 complete - candidates can use Test mode for learning with immediate feedback

---

## Phase 6: User Story 4 - Candidate Views Attempt History (Priority: P4)

**Goal**: Display chronological attempt history with detailed per-question breakdown and CSV/PDF downloads

**Independent Test**: Pre-populate 10 attempts, candidate views dashboard, drills into details, downloads CSV/PDF reports

### Implementation for User Story 4

- [ ] T092 [P] [US4] Create backend/src/services/export_service.py with generate_csv(attempt) using stdlib csv.DictWriter
- [ ] T093 [P] [US4] Create backend/src/services/export_service.py generate_pdf(attempt) using ReportLab with formatted table
- [ ] T094 [P] [US4] Create backend/src/api/results.py GET /results/attempts endpoint to list candidate's attempts (GSI3 query)
- [ ] T095 [US4] Create backend/src/api/results.py GET /results/attempts/{id} endpoint with per-question breakdown
- [ ] T096 [US4] Create backend/src/api/results.py GET /results/attempts/{id}/export/csv endpoint returning CSV file with Content-Disposition header
- [ ] T097 [US4] Create backend/src/api/results.py GET /results/attempts/{id}/export/pdf endpoint returning PDF file with Content-Disposition header
- [ ] T098 [P] [US4] Create frontend/src/components/candidate/AttemptHistory.jsx table with date, project, mode, score, actions
- [ ] T099 [P] [US4] Create frontend/src/components/candidate/AttemptDetail.jsx showing per-question breakdown with time spent
- [ ] T100 [US4] Create frontend/src/services/resultService.js with API calls: listAttempts, getAttemptDetail, downloadCSV, downloadPDF
- [ ] T101 [US4] Implement CSV download in frontend/src/components/candidate/AttemptDetail.jsx using fetch + Blob + downloadable link
- [ ] T102 [US4] Implement PDF download in frontend/src/components/candidate/AttemptDetail.jsx using fetch + Blob + downloadable link
- [ ] T103 [US4] Add empty state handling in frontend/src/components/candidate/AttemptHistory.jsx when no attempts exist
- [ ] T104 [US4] Add pagination in frontend/src/components/candidate/AttemptHistory.jsx for candidates with 50+ attempts

**Checkpoint**: User Story 4 complete - candidates can review history and export detailed reports

---

## Phase 7: User Story 5 - Admin Monitors Results (Priority: P5)

**Goal**: Provide aggregated analytics dashboard for admins with filtering and bulk export

**Independent Test**: Pre-populate 50 attempts, admin filters by project/date, views aggregated stats, downloads bulk report

### Implementation for User Story 5

- [ ] T105 [P] [US5] Update backend/src/api/results.py GET /results/attempts to support admin role with query params (project_id, date_range, candidate_email)
- [ ] T106 [US5] Create backend/src/api/results.py GET /results/stats endpoint for aggregated statistics (admin-only, RBAC check)
- [ ] T107 [US5] Implement aggregation logic in backend/src/services/exam_service.py: average score, completion rate, per-question % correct
- [ ] T108 [P] [US5] Create frontend/src/components/admin/ResultsDashboard.jsx with filters (project, date range, candidate)
- [ ] T109 [US5] Create frontend/src/components/admin/AggregatedStats.jsx displaying total attempts, avg score, completion rate
- [ ] T110 [US5] Create frontend/src/components/admin/QuestionStatistics.jsx table showing per-question difficulty (% correct, avg time)
- [ ] T111 [US5] Implement filter application in frontend/src/components/admin/ResultsDashboard.jsx with API call on filter change
- [ ] T112 [US5] Add bulk CSV export in frontend/src/components/admin/ResultsDashboard.jsx to download filtered attempts

**Checkpoint**: User Story 5 complete - admins have comprehensive results monitoring tools

---

## Phase 8: Authentication & User Management (Cross-Cutting)

**Purpose**: Complete auth flows not covered by foundational phase

- [ ] T113 [P] Create backend/src/api/auth.py POST /auth/register endpoint integrating with Cognito CreateUser API
- [ ] T114 [P] Create backend/src/api/auth.py POST /auth/login endpoint integrating with Cognito InitiateAuth API
- [ ] T115 [P] Create backend/src/api/auth.py POST /auth/refresh endpoint using Cognito refresh token flow
- [ ] T116 [P] Create frontend/src/components/auth/LoginForm.jsx with email/password fields and validation
- [ ] T117 [P] Create frontend/src/components/auth/RegisterForm.jsx with role selection (Admin/Candidate) and password strength meter
- [ ] T118 [P] Create frontend/src/services/authService.js with login, register, logout, refreshToken methods
- [ ] T119 [P] Create frontend/src/pages/LoginPage.jsx with tab switching between login and register forms
- [ ] T120 Implement automatic token refresh in frontend/src/services/api.js interceptor when 401 responses detected
- [ ] T121 Add password validation in frontend/src/components/auth/RegisterForm.jsx: min 8 chars, 1 uppercase, 1 lowercase, 1 number

---

## Phase 9: Testing & Quality Assurance

**Purpose**: Comprehensive testing across all user stories and edge cases

### Unit Tests (Backend)

- [ ] T122 [P] Create backend/tests/unit/test_pdf_service.py with tests for pypdf extraction, pdfplumber fallback, validation
- [ ] T123 [P] Create backend/tests/unit/test_question_service.py with tests for duplicate detection, random selection (no repeats)
- [ ] T124 [P] Create backend/tests/unit/test_exam_service.py with tests for scoring algorithm, timer validation, session state
- [ ] T125 [P] Create backend/tests/unit/test_export_service.py with tests for CSV generation, PDF generation (50 questions <2s)

### Contract Tests (Backend)

- [ ] T126 [P] Create backend/tests/contract/test_auth_contract.py validating auth-api.yaml endpoints (register, login, refresh)
- [ ] T127 [P] Create backend/tests/contract/test_projects_contract.py validating projects-api.yaml endpoints (CRUD operations)
- [ ] T128 [P] Create backend/tests/contract/test_questions_contract.py validating questions-api.yaml endpoints (CRUD, PDF upload)
- [ ] T129 [P] Create backend/tests/contract/test_exams_contract.py validating exams-api.yaml endpoints (start, submit, review)
- [ ] T130 [P] Create backend/tests/contract/test_results_contract.py validating results-api.yaml endpoints (history, stats, export)

### Integration Tests (Backend)

- [ ] T131 Create backend/tests/integration/test_exam_flow.py end-to-end test: start exam → answer 20 questions → submit → verify score
- [ ] T132 Create backend/tests/integration/test_pdf_upload.py: upload PDF → trigger parser → verify questions in DynamoDB
- [ ] T133 Create backend/tests/integration/test_result_generation.py: complete exam → generate CSV → generate PDF → verify content

### Component Tests (Frontend)

- [ ] T134 [P] Create frontend/tests/components/Timer.test.jsx with tests for countdown accuracy, auto-advance on expiration
- [ ] T135 [P] Create frontend/tests/components/QuestionCard.test.jsx with tests for answer selection, Test mode highlighting
- [ ] T136 [P] Create frontend/tests/components/ExamControls.test.jsx with tests for button states (disabled/enabled), navigation

### Service Tests (Frontend)

- [ ] T137 [P] Create frontend/tests/services/examService.test.js with mocked API calls for exam flow
- [ ] T138 [P] Create frontend/tests/services/authService.test.js with mocked Cognito responses for login/register

### End-to-End Tests

- [ ] T139 Create E2E test: Admin creates project → uploads PDF → questions appear in list
- [ ] T140 Create E2E test: Candidate takes 10-question exam in Hard mode → completes in <6 minutes → sees correct score
- [ ] T141 Create E2E test: Candidate downloads CSV report → verify file contains correct data
- [ ] T142 Create E2E test: Mobile viewport (320px) → candidate completes exam without horizontal scrolling

---

## Phase 10: Deployment & Infrastructure

**Purpose**: Production deployment to AWS with monitoring and CI/CD

- [ ] T143 Create CloudFormation/Terraform scripts for S3 buckets, DynamoDB tables, Cognito User Pool in infrastructure/ directory
- [ ] T144 [P] Create .github/workflows/backend-tests.yml for CI pipeline running pytest on pull requests
- [ ] T145 [P] Create .github/workflows/frontend-tests.yml for CI pipeline running Jest tests on pull requests
- [ ] T146 Create .github/workflows/deploy.yml for CD pipeline: backend SAM deploy, frontend S3 sync on merge to main
- [ ] T147 Configure API Gateway custom domain with SSL certificate via AWS Certificate Manager
- [ ] T148 Create CloudFront distribution for frontend S3 bucket with HTTPS and caching configuration
- [ ] T149 [P] Create CloudWatch alarms for Lambda errors, API Gateway 5xx responses, DynamoDB throttling
- [ ] T150 [P] Configure Lambda provisioned concurrency for exam start/submit endpoints to reduce cold starts
- [ ] T151 Create AWS Systems Manager Parameter Store entries for secrets (Cognito client ID, S3 bucket names)
- [ ] T152 Update backend/template.yaml with environment variables referencing Parameter Store
- [ ] T153 Create deployment documentation in docs/deployment-guide.md with step-by-step AWS setup instructions

---

## Phase 11: Documentation & Polish

**Purpose**: Finalize documentation, accessibility, and UX improvements

- [ ] T154 [P] Create docs/architecture.md with system architecture diagram (frontend, Lambda, DynamoDB, S3, Cognito)
- [ ] T155 [P] Create docs/api-reference.md consolidating all OpenAPI specs with authentication requirements
- [ ] T156 [P] Create docs/pdf-format-guide.md with required PDF structure and sample template for admins
- [ ] T157 [P] Add accessibility attributes (ARIA labels) to frontend/src/components/candidate/QuestionCard.jsx for screen readers
- [ ] T158 [P] Run axe DevTools accessibility audit on all pages and fix WCAG 2.1 AA violations
- [ ] T159 [P] Add loading states in frontend/src/components/shared/LoadingSpinner.jsx for all async operations
- [ ] T160 [P] Add success/error toast notifications in frontend/src/App.jsx for user actions (project created, exam submitted)
- [ ] T161 Optimize frontend bundle size: code splitting for admin/candidate routes, lazy loading for PDFUpload component
- [ ] T162 Add Lighthouse performance audit and optimize to score >90 for mobile
- [ ] T163 [P] Create CONTRIBUTING.md with PR guidelines, code style, and testing requirements

---

## Dependencies & Execution Order

### User Story Completion Order (MVP First)

```
Phase 1: Setup
  ↓
Phase 2: Foundational (BLOCKING - must complete before user stories)
  ↓
Phase 3: US1 (P1 - Exam Taking) ← MVP CRITICAL
  ↓
Phase 4: US2 (P2 - Question Bank) ← MVP CRITICAL
  ↓
Phase 5: US3 (P3 - Practice Tests) ← Iteration 2
  ↓
Phase 6: US4 (P4 - Attempt History) ← Iteration 2
  ↓
Phase 7: US5 (P5 - Admin Analytics) ← Iteration 2
  ↓
Phase 8: Authentication (Cross-Cutting)
  ↓
Phase 9: Testing & QA
  ↓
Phase 10: Deployment
  ↓
Phase 11: Documentation & Polish
```

### Parallel Execution Opportunities

**Phase 2 (Foundational)**: Can parallelize infrastructure provisioning with model/middleware development
- Parallel Track A: T012-T016 (AWS resource provisioning)
- Parallel Track B: T017-T022 (Backend models and database clients)
- Parallel Track C: T026-T030 (Frontend foundation)

**Phase 3 (US1 - Exam Taking)**: Backend and frontend can develop in parallel with mock APIs
- Parallel Track A: T031-T037 (Backend exam endpoints)
- Parallel Track B: T038-T049 (Frontend exam components)
- Sequential: T050-T054 (Integration and error handling)

**Phase 4 (US2 - Question Bank)**: Backend services and frontend UI parallelizable
- Parallel Track A: T055-T071 (Backend PDF parsing, API endpoints, Lambda)
- Parallel Track B: T072-T084 (Frontend admin UI)

**Phase 9 (Testing)**: All test categories can run in parallel
- Parallel Track A: T122-T125 (Unit tests)
- Parallel Track B: T126-T130 (Contract tests)
- Parallel Track C: T134-T138 (Frontend tests)
- Sequential: T131-T133, T139-T142 (Integration and E2E tests require deployed system)

### Critical Path (MVP - Cannot be parallelized)

```
T001-T011 (Setup) → T012-T030 (Foundation) → T031-T054 (US1 Exam) → T055-T084 (US2 Questions) → T113-T121 (Auth) → T131-T133 (Integration Tests) → T143-T153 (Deployment)
```

Estimated MVP timeline: **8-10 weeks** for 2 full-time developers with parallel execution

---

## Task Summary

**Total Tasks**: 163

**By Phase**:
- Phase 1 (Setup): 11 tasks
- Phase 2 (Foundational): 19 tasks
- Phase 3 (US1 - Exam Taking): 24 tasks ← MVP
- Phase 4 (US2 - Question Bank): 30 tasks ← MVP
- Phase 5 (US3 - Practice Tests): 7 tasks
- Phase 6 (US4 - Attempt History): 13 tasks
- Phase 7 (US5 - Admin Analytics): 8 tasks
- Phase 8 (Authentication): 9 tasks
- Phase 9 (Testing): 21 tasks
- Phase 10 (Deployment): 11 tasks
- Phase 11 (Documentation): 10 tasks

**By User Story**:
- US1 (P1 - Exam Taking): 24 tasks - Core value proposition
- US2 (P2 - Question Bank): 30 tasks - Required for US1
- US3 (P3 - Practice Tests): 7 tasks - Learning mode
- US4 (P4 - Attempt History): 13 tasks - Progress tracking
- US5 (P5 - Admin Analytics): 8 tasks - Management oversight

**Parallelizable Tasks**: 78 tasks (48% of total) marked with [P]

**MVP Scope**: Phases 1, 2, 3, 4, 8 = 93 tasks (57% of total)

---

## Implementation Strategy

### MVP Delivery (Phases 1-4 + 8)

**Goal**: Deliver working exam platform where:
- Candidates can take timed exams with scoring
- Admins can upload PDF questions or manually enter them

**Focus**: 93 tasks covering US1 (Exam Taking) + US2 (Question Bank) + Authentication

**Timeline**: 8-10 weeks for 2 developers

**Order**:
1. Complete Phase 1 (Setup) - 1 week
2. Complete Phase 2 (Foundational) - 2 weeks
3. Parallel: US1 backend (T031-T037) + US1 frontend (T038-T049) - 2 weeks
4. Integration: US1 testing (T050-T054) - 1 week
5. Parallel: US2 backend (T055-T071) + US2 frontend (T072-T084) - 3 weeks
6. Complete Phase 8 (Authentication) - 1 week
7. Integration testing + deployment prep - 1 week

### Iteration 2 (Phases 5-7)

**Goal**: Add practice mode, history tracking, admin analytics

**Focus**: 28 tasks covering US3 + US4 + US5

**Timeline**: 3-4 weeks

### Final Polish (Phases 9-11)

**Goal**: Comprehensive testing, production deployment, documentation

**Focus**: 42 tasks covering testing, deployment, documentation

**Timeline**: 2-3 weeks

---

## Validation Checklist

✅ **Format Compliance**:
- All tasks use `- [ ] [ID] [P?] [Story?] Description` format
- Sequential Task IDs (T001-T163)
- [P] marker only on parallelizable tasks
- [Story] labels (US1-US5) on user story tasks
- File paths included in all descriptions

✅ **Organization**:
- Tasks grouped by user story priority (P1, P2, P3, P4, P5)
- Setup and Foundational phases precede user stories
- Each user story independently testable
- Clear checkpoints after each phase

✅ **Completeness**:
- All 5 user stories from spec.md covered
- All functional requirements (FR-001 to FR-065) mapped to tasks
- Constitution principles validated (mobile-first, API-first, serverless, security, performance)
- Testing tasks for unit, contract, integration, E2E levels

✅ **Dependencies**:
- Foundational phase blocks all user story work
- User stories ordered by priority (P1, P2 first)
- Critical path identified
- Parallel execution opportunities documented

**Ready for implementation**: Use this task list to begin development with `/speckit.implement` command

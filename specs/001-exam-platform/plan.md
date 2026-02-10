# Implementation Plan: ExamBuddy Online Exam Center Platform

**Branch**: `001-exam-platform` | **Date**: 2026-02-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-exam-platform/spec.md`

## Summary

ExamBuddy is a responsive web application enabling admins to create exam projects with PDF upload or manual question entry, and candidates to take timed exams/practice tests with per-question difficulty modes (Easy/Medium/Hard/Expert). The system generates detailed result dashboards, tracks attempt history, and supports downloadable CSV/PDF reports. The technical approach leverages React for mobile-first frontend, Python FastAPI for serverless backend APIs on AWS Lambda, S3 for PDF/result storage, and DynamoDB for structured data persistence.

## Technical Context

**Language/Version**: Python 3.11 for backend, JavaScript (ES2022) with React 18+ for frontend  
**Primary Dependencies**: FastAPI 0.104+ (backend API framework), React 18+ with React Router, AWS SDK for Python (boto3), PyPDF2/pdfplumber for PDF parsing, Pydantic for data validation  
**Storage**: AWS S3 for PDF files and result exports; DynamoDB for structured data (users, projects, questions, attempts); potential RDS PostgreSQL for complex relational queries if DynamoDB limitations arise  
**Testing**: pytest with pytest-asyncio for backend unit/integration tests, Jest + React Testing Library for frontend, AWS SAM CLI for local Lambda testing  
**Target Platform**: AWS Lambda (Python 3.11 runtime) for backend with API Gateway REST API, S3 + CloudFront for frontend static hosting, cross-browser support (Chrome, Firefox, Safari, Edge)  
**Project Type**: Web application (separate frontend and backend)  
**Performance Goals**: PDF parsing <3 sec for 50 Q&A, question loading <1 sec, answer submission <500ms, dashboard rendering <2 sec for 100 attempts, support 100 concurrent exams  
**Constraints**: Lambda timeout <15 min per function, stateless execution, cold start <2 sec for time-critical endpoints, mobile-responsive UI (320px-1024px+ viewports)  
**Scale/Scope**: Initial target 1000 active candidates, 50 projects, 5000 questions total, 10k monthly exam attempts, with architecture supporting 10x growth without major refactoring

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Mobile-First Responsiveness**: Feature design includes mobile viewport specifications (320px, 768px, 1024px) and touch-optimized interactions
  - ✓ Spec SC-006/SC-007 mandate mobile/tablet testing for all workflows
  - ✓ Design will include responsive breakpoints, touch-friendly button sizes (44x44px min)
- [x] **API-First Architecture**: All backend functionality exposed via documented RESTful APIs with contract test specifications
  - ✓ Spec requires separate frontend/backend (user story independence)
  - ✓ Phase 1 will generate OpenAPI contract specifications before implementation
- [x] **Serverless-Ready**: Functions designed for stateless execution, no persistent process assumptions, compliant with Lambda constraints
  - ✓ Technical Context specifies Lambda deployment with <15 min timeout
  - ✓ All persistent data uses S3/DynamoDB (no local filesystem assumptions)
- [x] **Secure by Default**: Authentication/authorization requirements defined, input validation planned, RBAC roles identified
  - ✓ Spec FR-001 to FR-005 define email/password auth with bcrypt hashing
  - ✓ Admin/Candidate roles separated, JWT/Cognito tokens required for all endpoints
  - ✓ FR-058 to FR-065 cover validation (PDF format, email, password strength, file size)
- [x] **Performance Targets**: Relevant performance metrics identified (PDF parsing, question loading, submission latency, dashboard generation)
  - ✓ Spec SC-001 to SC-005 set concrete targets: 3s PDF parsing, 1s loading, 500ms submission, 2s dashboard, 100 concurrent exams

**Violations Requiring Justification**: N/A - All constitutional principles align with feature requirements

## Project Structure

### Documentation (this feature)

```text
specs/001-exam-platform/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification (already created)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── auth-api.yaml
│   ├── projects-api.yaml
│   ├── questions-api.yaml
│   ├── exams-api.yaml
│   └── results-api.yaml
└── checklists/
    └── requirements.md  # Specification quality checklist (already created)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── auth.py          # Login, register, token refresh endpoints
│   │   ├── projects.py      # Project CRUD operations (admin)
│   │   ├── questions.py     # Question management + PDF parsing (admin)
│   │   ├── exams.py         # Exam session start, answer submission, review (candidate)
│   │   └── results.py       # Result retrieval, history, CSV/PDF generation (candidate/admin)
│   ├── models/
│   │   ├── user.py          # User entity with role enum
│   │   ├── project.py       # Project entity
│   │   ├── question.py      # Question entity with answer options
│   │   └── attempt.py       # Attempt entity with answer selections
│   ├── services/
│   │   ├── auth_service.py       # JWT/Cognito integration, password hashing
│   │   ├── pdf_service.py        # PDF parsing logic (PyPDF2/pdfplumber)
│   │   ├── question_service.py   # Duplicate detection, random selection
│   │   ├── exam_service.py       # Timer logic, scoring, review phase
│   │   └── export_service.py     # CSV/PDF generation for results
│   ├── database/
│   │   ├── dynamodb_client.py    # DynamoDB connection and query helpers
│   │   └── s3_client.py          # S3 upload/download helpers
│   ├── middleware/
│   │   ├── auth_middleware.py    # Token validation for all protected routes
│   │   └── error_handler.py      # Global error handling and logging
│   ├── config.py                 # Environment variables (S3 bucket names, DynamoDB tables)
│   └── main.py                   # FastAPI app initialization
├── tests/
│   ├── contract/
│   │   ├── test_auth_contract.py
│   │   ├── test_projects_contract.py
│   │   ├── test_questions_contract.py
│   │   ├── test_exams_contract.py
│   │   └── test_results_contract.py
│   ├── integration/
│   │   ├── test_exam_flow.py         # End-to-end exam taking flow
│   │   ├── test_pdf_upload.py        # PDF parsing integration
│   │   └── test_result_generation.py # CSV/PDF export integration
│   └── unit/
│       ├── test_pdf_service.py
│       ├── test_question_service.py
│       ├── test_exam_service.py
│       └── test_export_service.py
├── Dockerfile                    # Local development container
├── requirements.txt              # Python dependencies
├── template.yaml                 # AWS SAM template for Lambda deployment
└── README.md                     # Backend setup and deployment instructions

frontend/
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.jsx
│   │   │   └── RegisterForm.jsx
│   │   ├── admin/
│   │   │   ├── ProjectList.jsx
│   │   │   ├── ProjectForm.jsx
│   │   │   ├── QuestionList.jsx
│   │   │   ├── QuestionForm.jsx
│   │   │   ├── PDFUpload.jsx
│   │   │   └── AdminDashboard.jsx
│   │   ├── candidate/
│   │   │   ├── ProjectSelection.jsx
│   │   │   ├── ExamConfig.jsx        # Mode, difficulty, question count selection
│   │   │   ├── QuestionCard.jsx      # Single question with timer
│   │   │   ├── ExamControls.jsx      # Next, Submit, Cancel buttons
│   │   │   ├── ReviewPhase.jsx       # Post-exam review for Exam mode
│   │   │   ├── ResultSummary.jsx     # Score and per-question breakdown
│   │   │   ├── AttemptHistory.jsx    # Past attempts list
│   │   │   └── AttemptDetail.jsx     # Detailed view with download buttons
│   │   ├── shared/
│   │   │   ├── Timer.jsx             # Countdown timer component
│   │   │   ├── ProgressBar.jsx       # Question progress indicator
│   │   │   ├── ErrorBoundary.jsx     # Error handling
│   │   │   └── LoadingSpinner.jsx
│   │   └── layout/
│   │       ├── Header.jsx
│   │       ├── Sidebar.jsx
│   │       └── Footer.jsx
│   ├── pages/
│   │   ├── LoginPage.jsx
│   │   ├── DashboardPage.jsx        # Routes to AdminDashboard or AttemptHistory
│   │   ├── ExamPage.jsx             # Active exam session
│   │   └── ResultPage.jsx           # Result summary after exam
│   ├── services/
│   │   ├── api.js                   # Axios instance with auth interceptor
│   │   ├── authService.js           # Login, register, token management
│   │   ├── projectService.js        # Project API calls
│   │   ├── questionService.js       # Question management, PDF upload
│   │   ├── examService.js           # Exam start, answer submission
│   │   └── resultService.js         # Result retrieval, download CSV/PDF
│   ├── hooks/
│   │   ├── useAuth.js               # Authentication state management
│   │   ├── useTimer.js              # Timer logic with auto-advance
│   │   └── useExamSession.js        # Exam session state (questions, answers, timer)
│   ├── styles/
│   │   ├── global.css               # Base styles and responsive breakpoints
│   │   └── components/              # Component-specific CSS modules
│   ├── utils/
│   │   ├── validators.js            # Email, password validation helpers
│   │   └── formatters.js            # Date/time formatting for results
│   ├── App.jsx                      # Main app with routing
│   └── index.jsx                    # React root render
├── public/
│   └── index.html
├── tests/
│   ├── components/
│   │   ├── QuestionCard.test.jsx
│   │   ├── Timer.test.jsx
│   │   └── ExamControls.test.jsx
│   └── services/
│       └── examService.test.js
├── Dockerfile                       # Local development container
├── package.json
├── .env.example                     # Environment variables template
└── README.md                        # Frontend setup instructions

.github/
├── workflows/
│   ├── backend-tests.yml            # CI for backend pytest
│   ├── frontend-tests.yml           # CI for frontend Jest tests
│   └── deploy.yml                   # CD to AWS (Lambda + S3/CloudFront)
└── CONTRIBUTING.md

docs/
├── architecture.md                  # System architecture diagram and overview
├── api-reference.md                 # Consolidated API documentation
├── pdf-format-guide.md              # Required PDF format for question uploads
└── deployment-guide.md              # AWS setup and deployment instructions
```

**Structure Decision**: Web application structure selected based on frontend (React) + backend (FastAPI) requirement in spec. Frontend handles all UI rendering and user interactions; backend exposes stateless REST APIs for data operations. This separation enables independent development, testing, and scaling of each layer, and aligns with API-First Architecture principle.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A - No constitutional violations detected.

## Phase 0: Research & Discovery

**Goal**: Resolve all NEEDS CLARIFICATION markers from Technical Context and research best practices for chosen technologies.

### Research Tasks

The Technical Context section above has been pre-filled with concrete technology choices based on the user's explicit requirements (React, FastAPI, AWS Lambda, S3, Docker). No NEEDS CLARIFICATION markers exist. However, research is still required for implementation best practices:

1. **FastAPI + AWS Lambda integration**: Research serverless FastAPI deployment patterns (Mangum adapter, AWS SAM vs Serverless Framework)
2. **PDF parsing libraries**: Compare PyPDF2 vs pdfplumber vs pypdf for performance, format support, and structured Q&A extraction
3. **DynamoDB schema design**: Research single-table design patterns for User/Project/Question/Attempt entities with efficient query access patterns
4. **React timer optimization**: Research useEffect + setInterval patterns for accurate countdown timers without UI blocking
5. **JWT vs AWS Cognito**: Compare implementation complexity, cost, scalability, and feature parity (token refresh, password reset, MFA support)
6. **Frontend state management**: Research Context API vs Redux vs Zustand for exam session state (questions, answers, timer) with minimal re-renders
7. **CSV/PDF generation in Lambda**: Research libraries (pandas for CSV, ReportLab vs WeasyPrint for PDF) that work within Lambda memory limits
8. **S3 presigned URLs**: Research secure PDF upload patterns (direct browser → S3 with presigned POST URLs vs proxy through Lambda)

### Research Outputs

See [research.md](research.md) for detailed findings. Summary of decisions will be documented there after research agents complete.

## Phase 1: Design & Contracts

**Goal**: Define data model, API contracts, and quickstart guide based on research findings.

### Data Model

See [data-model.md](data-model.md) for comprehensive entity definitions. Summary:

**Core Entities**:
- **User**: `user_id` (PK), `email`, `password_hash`, `role` (Admin/Candidate), `created_at`, `last_login`
- **Project**: `project_id` (PK), `name`, `description`, `admin_id` (FK), `archived`, `created_at`, `updated_at`
- **Question**: `question_id` (PK), `project_id` (FK/GSI), `text`, `answer_options` (JSON array), `correct_answer_index`, `explanation`, `created_at`
- **Attempt**: `attempt_id` (PK), `candidate_id` (FK/GSI), `project_id` (FK), `mode` (Test/Exam), `difficulty` (Easy/Medium/Hard/Expert), `start_time`, `end_time`, `score`
- **AnswerSelection**: `selection_id` (PK), `attempt_id` (FK/GSI), `question_id` (FK), `selected_answer_index`, `time_spent_seconds`, `is_correct`, `timestamp`

**Key Relationships**:
- User (Admin) → Projects (1:N)
- Project → Questions (1:N)
- User (Candidate) → Attempts (1:N)
- Attempt → AnswerSelections (1:N)
- AnswerSelection → Question (N:1) for historical reference

### API Contracts

See [contracts/](contracts/) directory for OpenAPI YAML specifications. Summary:

**Auth API** (`auth-api.yaml`):
- `POST /auth/register` - Create new user account
- `POST /auth/login` - Authenticate and receive JWT token
- `POST /auth/refresh` - Refresh expired token

**Projects API** (`projects-api.yaml`):
- `GET /projects` - List all projects (filtered by `archived` param)
- `POST /projects` - Create new project (admin only)
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project (admin only)
- `DELETE /projects/{id}` - Delete project if no active attempts (admin only)

**Questions API** (`questions-api.yaml`):
- `GET /projects/{id}/questions` - List all questions in project
- `POST /projects/{id}/questions` - Manually add question (admin only)
- `POST /projects/{id}/questions/upload-pdf` - Upload PDF for parsing (admin only)
- `PUT /questions/{id}` - Update question (admin only)
- `DELETE /questions/{id}` - Delete question with confirmation (admin only)

**Exams API** (`exams-api.yaml`):
- `POST /exams/start` - Start new exam session with random question selection
- `POST /exams/{session_id}/answers` - Submit answer for current question
- `GET /exams/{session_id}/review` - Get review phase data (Exam mode only)
- `POST /exams/{session_id}/submit` - Finalize exam and calculate score
- `DELETE /exams/{session_id}` - Cancel exam (discard attempt)

**Results API** (`results-api.yaml`):
- `GET /results/attempts` - List all attempts for candidate (or all for admin with filters)
- `GET /results/attempts/{id}` - Get detailed attempt with per-question breakdown
- `GET /results/attempts/{id}/export/csv` - Download CSV report
- `GET /results/attempts/{id}/export/pdf` - Download PDF report
- `GET /results/stats` - Get aggregated statistics (admin only)

### Quickstart Guide

See [quickstart.md](quickstart.md) for detailed setup instructions. Summary:

**Local Development**:
1. Clone repo: `git clone <repo_url> && cd ExamBuddy`
2. Backend: `cd backend && docker-compose up` (FastAPI + DynamoDB Local + LocalStack S3)
3. Frontend: `cd frontend && npm install && npm start`
4. Access: Frontend at `http://localhost:3000`, Backend API at `http://localhost:8000/docs`

**AWS Deployment**:
1. Configure AWS CLI with credentials
2. Backend: `cd backend && sam build && sam deploy --guided`
3. Frontend: `cd frontend && npm run build && aws s3 sync build/ s3://exambuddy-frontend`
4. CloudFront: Create distribution pointing to S3 bucket

**First Steps**:
1. Register admin account via `/auth/register` with `role=Admin`
2. Login and navigate to Admin Dashboard
3. Create first project and upload sample PDF
4. Register candidate account and take practice exam

## Implementation Notes

**Phase 2 (Tasks Generation)**:
- When generating tasks.md, prioritize User Story 1 (P1: Exam Taking) and User Story 2 (P2: Question Bank) as MVP
- Defer User Stories 3-5 (Practice Tests, History, Admin Analytics) to iteration 2
- Foundational tasks: Docker setup, AWS resource provisioning (S3 buckets, DynamoDB tables, API Gateway), authentication middleware

**Phase 3 (Implementation)**:
- Backend implementation should start with contract tests (validate OpenAPI specs) before writing service logic
- Frontend should use mock API responses during parallel development (MSW - Mock Service Worker)
- PDF parsing requires performance profiling to meet <3 sec target (consider lazy parsing or chunking for large files)

**Phase 4 (Testing)**:
- Integration tests must validate: PDF upload → parsing → question storage → random selection → exam flow → score calculation → result export
- Load testing required for 100 concurrent exams (use Locust or k6 against Lambda endpoints)
- Mobile responsiveness testing on real devices (BrowserStack or physical devices) for 320px, 768px, 1024px breakpoints

**Phase 5 (Deployment)**:
- AWS SAM preferred over Serverless Framework for native Lambda integration
- Frontend CDN via CloudFront mandatory for global performance
- DynamoDB On-Demand billing recommended initially (predictable costs, no capacity planning)
- CloudWatch alarms for Lambda errors, API Gateway 5xx responses, DynamoDB throttling

## Dependencies & Prerequisites

**External Services**:
- AWS account with permissions for Lambda, API Gateway, S3, DynamoDB, CloudWatch, IAM
- Domain name for custom API Gateway endpoint (optional but recommended for production)
- SSL certificate via AWS Certificate Manager for HTTPS

**Development Tools**:
- Docker Desktop 20+ for local containerized development
- Node.js 18+ for frontend development
- Python 3.11+ for backend development (matching Lambda runtime)
- AWS CLI v2 for deployment
- AWS SAM CLI for local Lambda testing

**Third-Party Libraries**:
- Backend: FastAPI, boto3, PyPDF2/pdfplumber, pydantic, python-jose (JWT), passlib (password hashing), pytest
- Frontend: React, React Router, Axios, date-fns (date formatting), react-pdf (PDF preview for admins)

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| PDF parsing fails for non-standard formats | High - blocks admin question uploads | Medium | Document required PDF format clearly, validate early, provide sample PDF templates, add manual entry fallback |
| Lambda cold starts exceed 2 sec target | Medium - degrades exam start UX | Medium | Implement provisioned concurrency for exam endpoints, optimize bundle size, consider Lambda SnapStart (Python 3.11 support) |
| DynamoDB query patterns inefficient for complex filters (admin analytics) | Medium - slow admin dashboards | Low | Design GSIs carefully in data model phase, consider RDS PostgreSQL fallback for reporting if queries exceed 3 DynamoDB indexes |
| Timer accuracy issues (JavaScript setInterval drift) | High - invalidates timed exam fairness | Low | Use server-side timer validation (backend tracks question start time, validates submission timestamp), client timer is UI-only |
| Concurrent exam sessions exceed DynamoDB write capacity | High - exam submission failures | Low | Use DynamoDB On-Demand mode (auto-scaling), implement exponential backoff retry logic, monitor CloudWatch metrics |
| Mobile browsers block background timers (iOS Safari) | High - breaks exam flow on mobile | Medium | Use Web Locks API or Visibility API to detect tab switching, warn users, implement server-side timeout fallback |

## Success Metrics (Technical)

These complement the Success Criteria from the spec (SC-001 to SC-010) with implementation-specific metrics:

- **Code Coverage**: Backend ≥80% line coverage (pytest-cov), Frontend ≥70% (Jest coverage)
- **API Response Times**: p95 < 500ms for all endpoints under 100 concurrent users (monitored via CloudWatch)
- **Lambda Cold Start**: p95 < 2 sec for exam endpoints, p95 < 5 sec for admin endpoints (measured via X-Ray)
- **PDF Parsing Success Rate**: ≥95% for properly formatted PDFs (tracked via CloudWatch Logs Insights)
- **Frontend Bundle Size**: Initial load < 500KB gzipped (measured via Lighthouse)
- **Accessibility**: WCAG 2.1 AA compliance for all pages (validated via axe DevTools)
- **Error Rate**: < 1% of API requests result in 5xx errors (monitored via API Gateway metrics)

## Next Steps

1. **Complete Phase 0**: Research agents will investigate FastAPI Lambda patterns, PDF parsing libraries, DynamoDB design, and generate [research.md](research.md)
2. **Complete Phase 1**: After research, generate [data-model.md](data-model.md), [contracts/](contracts/) OpenAPI specs, and [quickstart.md](quickstart.md)
3. **Update Agent Context**: Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot` to add React, FastAPI, AWS Lambda to agent memory
4. **Re-evaluate Constitution Check**: Verify API contracts and data model comply with all 5 constitutional principles
5. **Proceed to Phase 2**: Run `/speckit.tasks` to generate implementation tasks organized by user story priority (P1, P2 first)

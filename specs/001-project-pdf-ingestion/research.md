# Phase 0 Research: Project PDF Question Ingestion

## Decision 1: PDF parsing pipeline and library choice
- Decision: Use a two-stage parser with `pdfplumber` for layout-preserving text extraction and `pypdf` as fallback text extractor for malformed pages.
- Rationale: `pdfplumber` handles structured exam-like PDFs better (line/region fidelity), while `pypdf` improves robustness when layout metadata is poor.
- Alternatives considered:
  - Use only `pypdf`: simpler but less accurate for table-like and multi-column question formats.
  - OCR-first approach: unnecessary complexity/cost for text-based PDFs and increases latency.

## Decision 2: Ingestion publication semantics
- Decision: Implement draft-to-published lifecycle (`DRAFT` -> `PROCESSING` -> `PUBLISHED` or `FAILED`) and expose status endpoint.
- Rationale: Prevents students from seeing partial/invalid banks and provides clear admin recovery path.
- Alternatives considered:
  - Immediate publish on upload: risks exposing partially parsed content.
  - Manual publish-only flow: safer but adds operational overhead for initial release.

## Decision 3: Data persistence model
- Decision: Persist project metadata and normalized question/answer records in DynamoDB; store uploaded source PDFs in S3.
- Rationale: Aligns with existing serverless stack, minimizes operational overhead, supports project-scoped query patterns.
- Alternatives considered:
  - Relational DB migration: stronger joins but out of scope and infrastructure-heavy.
  - Store full parsed payload only in S3: weak queryability for session start/scoring.

## Decision 4: Student project visibility rules
- Decision: Student list endpoint returns only `PUBLISHED` and `ACTIVE` projects with at least one valid parsed question.
- Rationale: Enforces FR-006 and reduces start-session failures.
- Alternatives considered:
  - Return all projects with frontend filtering: leaks admin states and weakens API boundary.
  - Include `PROCESSING` projects: causes unpredictable UX and start failures.

## Decision 5: Session project pinning
- Decision: Pin selected `project_id` and question ID set at session creation; scoring uses persisted `AnswerKey` by question ID.
- Rationale: Guarantees project consistency through exam lifecycle and directly satisfies FR-008/FR-009.
- Alternatives considered:
  - Resolve questions dynamically during submit: vulnerable to mid-session project edits.
  - Cache answer keys client-side: weak trust model and security risk.

## Decision 6: Validation and limits
- Decision: Enforce upload constraints (`application/pdf`, configurable max size, minimum one valid Q/A pair) and atomic publish behavior.
- Rationale: Prevents malformed ingestion and supports clear error handling per FR-005.
- Alternatives considered:
  - Lenient parse with partial publish: increases hidden data quality issues.
  - No size/type guardrails: increases Lambda timeout/failure risk.

## Decision 7: Audit and observability
- Decision: Emit structured audit events for project creation, ingestion start/result, and session start including actor role and project ID.
- Rationale: Satisfies FR-010 and improves supportability in production.
- Alternatives considered:
  - Basic text logs only: harder to trace and analyze.
  - Full event bus integration now: valuable but unnecessary for first implementation phase.

## Resolved Clarifications
- No remaining `NEEDS CLARIFICATION` items from technical context.
- Existing technology baseline remains unchanged: FastAPI + Lambda/API Gateway + DynamoDB/S3 + React/Vite.

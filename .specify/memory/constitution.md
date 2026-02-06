<!--
Sync Impact Report - Version 1.0.0
================================================
VERSION CHANGE: (new) → 1.0.0
BUMP RATIONALE: Initial constitution for ExamBuddy project
MODIFIED PRINCIPLES: None (initial creation)
ADDED SECTIONS:
  - Core Principles (5 principles)
  - Security & Compliance
  - Development Workflow
  - Governance
REMOVED SECTIONS: None
TEMPLATES STATUS:
  ✅ .specify/templates/plan-template.md - Constitution Check section aligns
  ✅ .specify/templates/spec-template.md - Requirements structure compatible
  ✅ .specify/templates/tasks-template.md - Phase organization compatible
FOLLOW-UP TODOS: None
================================================
-->

# ExamBuddy Constitution

## Core Principles

### I. Mobile-First Responsiveness

The ExamBuddy platform MUST prioritize mobile responsiveness across all user interfaces. Every feature, component, and page MUST be fully functional and optimally displayed on mobile devices (smartphones, tablets) as well as desktop browsers.

**Rationale**: Candidates taking exams need flexibility to access the platform from any device, anywhere. Admin functions must also be accessible on-the-go for monitoring and content management.

**Testing Requirements**:
- All UI components MUST be tested on viewport widths: 320px (mobile), 768px (tablet), 1024px (desktop)
- Touch interactions MUST be optimized with appropriate tap target sizes (minimum 44x44px)
- No horizontal scrolling permitted on mobile viewports

### II. API-First Architecture

All backend functionality MUST be exposed through well-defined RESTful API endpoints. The frontend MUST communicate with the backend exclusively through these APIs, with no direct database access or server-side rendering dependencies.

**Rationale**: Enables clean separation of concerns, allows independent frontend/backend development and testing, supports future mobile app development, and facilitates serverless deployment on AWS Lambda.

**Requirements**:
- All endpoints MUST be documented with request/response schemas
- Contract tests MUST validate API specifications before implementation
- APIs MUST return consistent error responses with appropriate HTTP status codes
- All endpoints MUST support JSON request/response format

### III. Serverless-Ready Design (NON-NEGOTIABLE)

All backend services MUST be designed for stateless, serverless execution on AWS Lambda. Code MUST avoid assumptions about persistent processes, local file systems (except `/tmp`), or long-running connections.

**Rationale**: AWS Lambda provides cost-effective scaling, eliminates server maintenance, and ensures ExamBuddy can handle variable exam traffic patterns without over-provisioning infrastructure.

**Requirements**:
- Functions MUST complete within Lambda timeout limits (<15 minutes)
- Persistent data MUST use S3, DynamoDB, or external databases
- Environment configuration MUST use Lambda environment variables or AWS Systems Manager Parameter Store
- Cold start optimization MUST be considered for time-critical endpoints

### IV. Secure by Default

Authentication and authorization MUST be enforced at every layer. User data, exam results, and admin operations MUST be protected with industry-standard security practices.

**Rationale**: ExamBuddy handles sensitive candidate data and exam content that must be protected from unauthorized access, tampering, and data breaches.

**Requirements**:
- All API endpoints (except public login/register) MUST require valid authentication tokens
- Passwords MUST be hashed using bcrypt or argon2 (never stored in plain text)
- JWT tokens or AWS Cognito sessions MUST expire and support refresh mechanisms
- Role-based access control (RBAC) MUST separate Admin and Candidate permissions
- All S3 uploads MUST be validated for file type and size
- SQL injection and XSS prevention MUST be implemented

### V. Performance & Scalability

The system MUST meet performance targets for PDF parsing, question loading, and result generation to ensure smooth user experience even under load.

**Rationale**: Slow loading times frustrate users and can invalidate timed exam results. The system must scale to handle multiple concurrent exams.

**Performance Targets**:
- PDF parsing: <3 seconds for 50 question-answer pairs
- Question loading for exam start: <1 second
- Answer submission and validation: <500ms per question
- Dashboard generation: <2 seconds for 100 attempts
- Support at least 100 concurrent active exams

## Security & Compliance

**Data Encryption**:
- Data in transit MUST use HTTPS/TLS 1.2+ for all API communications
- Sensitive data at rest (S3) MUST use server-side encryption (SSE-S3 or SSE-KMS)

**Access Control**:
- Admins MUST NOT access candidate passwords or authentication tokens
- Candidates MUST only access their own attempt history and results
- Admin operations (create/edit/delete projects, upload PDFs) MUST be restricted to admin role

**Data Retention**:
- PDF files and exam results MUST be retained in S3 with versioning enabled
- Audit logs MUST track all admin modifications to projects and questions

**Validation**:
- All file uploads MUST validate PDF format before processing
- Duplicate question detection MUST prevent accidental re-uploads
- Input sanitization MUST be applied to all user-provided text fields

## Development Workflow

**Test Coverage Requirements**:
- All API endpoints MUST have contract tests
- Critical user flows (exam taking, result submission) MUST have integration tests
- Unit tests MUST cover business logic (scoring, timer calculations, question randomization)

**Code Review Gates**:
- All PRs MUST pass automated tests before merge
- Security-sensitive changes (authentication, authorization, file uploads) MUST have manual security review
- Performance-critical paths (PDF parsing, exam loading) MUST include performance benchmarks

**Docker & Local Development**:
- Backend MUST provide Docker Compose setup for local development with hot-reload
- Frontend MUST support local development server with mock API or local backend
- Environment variables MUST be documented with example `.env` file

**Deployment**:
- Backend MUST be packaged as Lambda deployment artifacts (ZIP or container images)
- Frontend MUST be deployable to S3 + CloudFront or similar static hosting
- Infrastructure as Code (Terraform or CloudFormation) recommended but not mandatory for initial version

## Governance

This constitution supersedes all other development practices. When conflicts arise between this document and other guidelines, the constitution takes precedence.

**Amendment Process**:
- Constitution changes MUST be documented with version bump rationale
- Breaking changes to core principles require MAJOR version increment
- New principles or sections require MINOR version increment
- Clarifications and wording improvements require PATCH version increment
- All amendments MUST update the Sync Impact Report comment at the top of this file

**Compliance Verification**:
- All feature specifications MUST include a Constitution Check section referencing relevant principles
- Implementation plans MUST justify any deviations from core principles with documented complexity rationale
- Code reviews MUST verify adherence to security, performance, and architectural principles

**Runtime Guidance**:
- For development execution guidance, refer to `.specify/templates/` for workflow templates
- For agent-specific instructions, refer to `.github/prompts/` command definitions

**Version**: 1.0.0 | **Ratified**: 2026-02-06 | **Last Amended**: 2026-02-06

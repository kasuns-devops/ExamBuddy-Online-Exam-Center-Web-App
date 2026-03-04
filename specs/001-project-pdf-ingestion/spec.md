# Feature Specification: Project PDF Question Ingestion

**Feature Branch**: `001-project-pdf-ingestion`  
**Created**: 2026-03-04  
**Status**: Draft  
**Input**: User description: "admin user create a project and pdf is uploaded with questions and answers, and those answers save in database, and let student user select project from available projects and start test or exam"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Admin uploads project question set (Priority: P1)

An admin creates a new project, uploads a PDF containing questions and answers, and the system stores parsed questions with correct answers for later exam delivery.

**Why this priority**: Without this flow, no valid project question bank exists for students.

**Independent Test**: Can be fully tested by creating a project with a valid PDF and verifying that questions and correct answers are persisted and retrievable for that project.

**Acceptance Scenarios**:

1. **Given** an authenticated admin and a valid project PDF, **When** the admin creates a project and uploads the file, **Then** the project is created and parsed questions with answers are saved.
2. **Given** an authenticated admin and an invalid or unparseable PDF, **When** upload is submitted, **Then** project ingestion fails gracefully with a clear error and no partial corrupted question set is published.

---

### User Story 2 - Student selects an available project (Priority: P2)

A student views available projects and chooses one that has published questions.

**Why this priority**: Students must be able to discover and enter the correct project before taking any assessment.

**Independent Test**: Can be tested by loading the project list as a student and confirming only available projects with usable question banks are selectable.

**Acceptance Scenarios**:

1. **Given** at least one published project, **When** a student opens project selection, **Then** the available projects are listed with enough metadata to choose.
2. **Given** no published projects, **When** a student opens project selection, **Then** a clear empty-state message is shown and exam start is blocked.

---

### User Story 3 - Student starts test or exam from selected project (Priority: P3)

After choosing a project, a student can start either test mode or exam mode using that project’s stored question bank.

**Why this priority**: This delivers the student-facing outcome of the uploaded content.

**Independent Test**: Can be tested by selecting one project and starting both test and exam sessions, verifying delivered questions come from that project and scoring uses stored answers.

**Acceptance Scenarios**:

1. **Given** a student-selected project with saved questions, **When** the student starts test mode, **Then** the session loads questions from that project and supports immediate feedback flow.
2. **Given** a student-selected project with saved questions, **When** the student starts exam mode, **Then** the session loads questions from that project and supports full exam submission/review flow.

### Edge Cases

- PDF contains duplicate questions or conflicting answer keys.
- PDF parsing succeeds but yields zero valid question-answer pairs.
- Admin uploads a very large file that exceeds allowed limits.
- Admin attempts upload with missing project name or missing file.
- Student tries to start a session for a project that was unpublished/deleted after list load.
- Student starts exam while another session is already active for the same project.

### Assumptions

- Admin and student roles already exist and are enforceable by the system.
- PDF files follow a supported question-answer structure for parser recognition.
- Only published/active projects are visible to students.
- Existing test mode and exam mode session behavior remains unchanged except for project sourcing.

### Dependencies

- Availability of PDF parsing capability for structured question-answer extraction.
- Persistent storage for projects, parsed questions, and answer keys.
- Existing authentication/authorization infrastructure for role-based actions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow an authenticated admin to create a project with required metadata before or during PDF upload.
- **FR-002**: System MUST accept a PDF upload for an admin-created project and process it as a project question source.
- **FR-003**: System MUST extract questions and their corresponding correct answers from supported PDF content and associate them with the target project.
- **FR-004**: System MUST persist extracted questions and correct answers so they are available for future student sessions.
- **FR-005**: System MUST reject uploads that cannot be parsed into at least one valid question-answer pair and return a user-readable error.
- **FR-006**: System MUST prevent students from seeing or selecting projects that do not have a valid published question bank.
- **FR-007**: System MUST allow a student to select from available projects and start either test mode or exam mode.
- **FR-008**: System MUST ensure all questions delivered in a student session originate from the selected project.
- **FR-009**: System MUST evaluate student answers against the persisted answer keys for that project during scoring/feedback.
- **FR-010**: System MUST log project creation and upload processing outcomes for audit and support troubleshooting.

### Key Entities *(include if feature involves data)*

- **Project**: Represents an assessment collection owned by admins, including title, status, and availability to students.
- **ProjectDocument**: Represents an uploaded PDF source file and processing status for a specific project.
- **QuestionItem**: Represents a parsed question linked to a project, including prompt, type, options (if applicable), and sequence.
- **AnswerKey**: Represents the correct answer representation tied to a question item and used for scoring.
- **StudentSession**: Represents a student’s started test/exam attempt for a selected project, including delivered questions and outcome state.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of valid admin PDF uploads produce a published project question bank without manual intervention.
- **SC-002**: 100% of student sessions started from a selected project contain only questions belonging to that project.
- **SC-003**: 100% of graded responses in test/exam sessions are evaluated against stored answer keys linked to the selected project.
- **SC-004**: Students can select a project and start a test/exam in under 30 seconds for at least 90% of attempts.

# Feature Specification: ExamBuddy Online Exam Center Platform

**Feature Branch**: `001-exam-platform`  
**Created**: 2026-02-06  
**Status**: Draft  
**Input**: User description: "Online Exam Center Web App with admin project management, PDF upload, question bank, timed exams/tests with difficulty modes, result dashboards, and attempt history tracking"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Candidate Takes Timed Exam (Priority: P1)

A candidate logs in, selects a project, chooses exam mode with difficulty level and number of questions, answers questions under timed conditions, and receives immediate scoring with detailed feedback upon completion.

**Why this priority**: This is the core value proposition - delivering functional online exams. Without this, ExamBuddy has no viable product.

**Independent Test**: Can be fully tested by pre-loading a question bank, having a candidate complete one exam session, and verifying score calculation and result display without any other features enabled.

**Acceptance Scenarios**:

1. **Given** candidate is logged in and a project with 50 questions exists, **When** candidate selects 20 questions in Hard mode (30 sec per question), **Then** system randomly selects 20 unique questions and starts timer for first question
2. **Given** candidate is answering question 5 of 20 in Medium mode, **When** timer expires (1 minute), **Then** system auto-advances to next question and marks previous question as unanswered
3. **Given** candidate has answered all questions in exam mode, **When** candidate clicks review phase, **Then** system displays each question for half the original timer duration (review-only, no changes allowed)
4. **Given** candidate completes review phase and clicks Submit, **When** system calculates score, **Then** candidate sees total score, per-question correctness, and time spent per question
5. **Given** candidate cancels mid-exam, **When** candidate confirms cancellation, **Then** system discards attempt (not saved to history) and returns to project selection

---

### User Story 2 - Admin Manages Question Bank (Priority: P2)

An admin logs in, creates a project, uploads a PDF containing questions and answers, and the system validates format, detects duplicates, and stores questions separately from answers for secure exam delivery.

**Why this priority**: Without a question bank, there are no exams to take. This is the second most critical feature after exam delivery itself.

**Independent Test**: Can be fully tested by admin uploading a 50-question PDF, verifying duplicate detection, manually entering additional questions, and confirming all questions are retrievable and properly formatted without implementing exam-taking functionality.

**Acceptance Scenarios**:

1. **Given** admin is logged in, **When** admin creates a new project with name "AWS Certification Prep", **Then** system creates empty project and displays question management interface
2. **Given** admin is in project management view, **When** admin uploads a valid PDF with 30 Q&A pairs, **Then** system parses PDF within 3 seconds, validates format, detects 0 duplicates, and stores questions/answers separately
3. **Given** admin uploads PDF with duplicate questions, **When** system detects 5 duplicates, **Then** system displays warning with duplicate question previews and option to skip or overwrite
4. **Given** admin is viewing project question list, **When** admin manually enters a new question with 4 answer options and marks correct answer, **Then** system validates all required fields and adds question to project
5. **Given** admin is editing a question, **When** admin modifies question text or answers and saves, **Then** system updates question and maintains question ID for historical attempt integrity
6. **Given** admin selects a question, **When** admin clicks delete, **Then** system confirms deletion (warning about impact on historical attempts) and removes question from active bank

---

### User Story 3 - Candidate Takes Practice Test with Immediate Feedback (Priority: P3)

A candidate logs in, selects test mode (instead of exam mode), answers questions with immediate correct answer highlighting after each response, and navigates freely to review understanding without time pressure impacting their learning.

**Why this priority**: Test mode supports learning and practice before taking graded exams. It's valuable but not critical for the initial MVP since exam mode already delivers assessment functionality.

**Independent Test**: Can be fully tested by pre-loading questions, having candidate select test mode, answering questions one-by-one with immediate feedback display, and verifying the experience is distinctly different from exam mode (immediate feedback vs. deferred review).

**Acceptance Scenarios**:

1. **Given** candidate is logged in and selects test mode with Easy difficulty (2 min per question), **When** candidate selects an answer, **Then** system immediately highlights correct answer in green and shows Next button (no Submit or review phase)
2. **Given** candidate is in test mode and answers question incorrectly, **When** correct answer is highlighted, **Then** candidate can review both their selected answer (marked incorrect) and correct answer before clicking Next
3. **Given** candidate has completed 15 of 20 test mode questions, **When** candidate clicks Cancel, **Then** system discards session (not saved to history) and returns to project selection
4. **Given** candidate completes all test mode questions, **When** candidate clicks Finish on last question, **Then** system displays summary score and per-question breakdown (same as exam mode results)

---

### User Story 4 - Candidate Views Attempt History Dashboard (Priority: P4)

A candidate logs in and accesses their personalized dashboard showing all past exam/test attempts with date/time, mode, score, questions attempted, and downloadable detailed reports in CSV/PDF format.

**Why this priority**: Historical tracking enables progress monitoring and performance analysis, but the system can function without it initially. Users can take exams and see immediate results without needing historical dashboards.

**Independent Test**: Can be fully tested by pre-populating 10 historical attempts for a candidate, verifying dashboard displays all attempts with correct metadata, allowing candidate to download CSV/PDF reports, and drill into individual attempt details without requiring any other feature to be active.

**Acceptance Scenarios**:

1. **Given** candidate is logged in and has completed 5 exams across 3 projects, **When** candidate navigates to dashboard, **Then** system displays chronological list of all attempts with date/time, project name, mode, score, and questions attempted
2. **Given** candidate is viewing dashboard, **When** candidate clicks on a specific attempt, **Then** system displays detailed view with per-question breakdown: question text, selected answer, correct answer, time spent, correctness indicator
3. **Given** candidate is viewing attempt details, **When** candidate clicks Download CSV, **Then** system generates CSV file with columns: question_number, question_text, selected_answer, correct_answer, time_spent_seconds, is_correct, timestamp
4. **Given** candidate is viewing attempt details, **When** candidate clicks Download PDF, **Then** system generates formatted PDF report with header (candidate name, project, date), summary section (score, time, mode), and per-question breakdown table
5. **Given** candidate has no attempt history, **When** candidate navigates to dashboard, **Then** system displays empty state message "No attempts yet. Start your first exam!" with link to project selection

---

### User Story 5 - Admin Monitors Candidate Results (Priority: P5)

An admin logs in and accesses aggregated dashboards showing all candidate attempts across all projects, with filtering by project, date range, and candidate, enabling performance monitoring and content quality assessment.

**Why this priority**: Admin analytics are valuable for long-term platform management but not required for the core exam delivery functionality. Individual candidates can already see their own results, so this is purely an administrative convenience feature.

**Independent Test**: Can be fully tested by pre-populating 50 candidate attempts across multiple projects, verifying admin can filter by project/date/candidate, view aggregated statistics (average score, completion rate, question difficulty analysis), and download reports without impacting candidate-facing functionality.

**Acceptance Scenarios**:

1. **Given** admin is logged in, **When** admin navigates to results dashboard, **Then** system displays aggregated view of all attempts with filters for project, date range, and candidate email
2. **Given** admin applies filter "Project: AWS Certification, Last 30 days", **When** system loads filtered results, **Then** admin sees total attempts, average score, completion rate, and per-question statistics (% correct, average time)
3. **Given** admin is viewing per-question statistics, **When** admin identifies questions with <40% correct rate, **Then** admin can flag questions for review or modification
4. **Given** admin is viewing results dashboard, **When** admin clicks Download Report, **Then** system generates CSV with all attempts in filtered view including candidate email, project, date, score, mode, questions attempted

---

### Edge Cases

- What happens when candidate loses internet connection mid-exam? System should detect disconnection, pause timer, and either resume from last saved state or mark attempt as incomplete if reconnection exceeds timeout threshold.
- What happens when two admins simultaneously edit the same question? System should implement optimistic locking or last-write-wins with timestamp-based conflict detection and notification.
- What happens when admin deletes a project with active exam sessions? System should prevent deletion if any candidate has an in-progress attempt, or force-cancel active attempts with notification.
- What happens when PDF contains malformed questions (missing answers, incorrect formatting)? System should validate structure, report specific line/page errors, and reject upload with actionable error messages.
- What happens when candidate selects more questions than available in project (e.g., requests 50 questions but only 30 exist)? System should display error "Only 30 questions available. Please select up to 30." and prevent exam start.
- What happens when timer reaches 0 on last question in exam mode? System should auto-advance to review phase or auto-submit if review phase is also complete.
- What happens when candidate clicks browser back button during exam? System should prevent navigation with confirmation dialog "Exam in progress. Clicking back will cancel your attempt."
- What happens when admin uploads 500-question PDF? System should enforce file size limits (e.g., max 10MB or 200 questions) and display error with guidance to split into multiple uploads.

## Requirements *(mandatory)*

### Functional Requirements

**Authentication & Authorization**

- **FR-001**: System MUST authenticate users via email and password with bcrypt/argon2 hashed passwords stored securely
- **FR-002**: System MUST support two distinct roles: Admin and Candidate with role-based access control enforced at API layer
- **FR-003**: System MUST provide separate dashboards for Admin (project management, results monitoring) and Candidate (exam taking, personal history)
- **FR-004**: System MUST require authentication token (JWT or AWS Cognito session) for all API requests except login/register endpoints
- **FR-005**: System MUST expire authentication tokens after 24 hours of inactivity and require re-login

**Project Management (Admin)**

- **FR-006**: Admin MUST be able to create new projects with name and optional description fields (max 200 characters)
- **FR-007**: Admin MUST be able to edit project name and description without affecting existing questions or candidate attempt history
- **FR-008**: Admin MUST be able to delete projects only if no candidate has active in-progress attempts
- **FR-009**: System MUST display project list with question count and last modified timestamp for each project
- **FR-010**: Admin MUST be able to archive projects (hide from candidate selection) without deleting historical data

**Question Bank Management (Admin)**

- **FR-011**: Admin MUST be able to upload PDF files containing questions and answers with automatic parsing
- **FR-012**: System MUST validate PDF format and reject uploads that don't contain parseable text (scanned images without OCR are invalid)
- **FR-013**: System MUST parse PDF and extract questions with multiple-choice answers (minimum 2 options, maximum 6 options per question)
- **FR-014**: System MUST complete PDF parsing within 3 seconds for files containing up to 50 question-answer pairs
- **FR-015**: System MUST detect duplicate questions by comparing question text (case-insensitive, whitespace-normalized) and prompt admin to skip or overwrite
- **FR-016**: System MUST store questions and answers in separate data structures to prevent answer leakage in candidate-facing APIs
- **FR-017**: Admin MUST be able to manually enter questions with fields: question text (max 500 chars), 2-6 answer options (max 200 chars each), correct answer indicator, optional explanation (max 1000 chars)
- **FR-018**: Admin MUST be able to edit existing questions while preserving question ID for historical attempt integrity
- **FR-019**: Admin MUST be able to delete questions with confirmation dialog warning about impact on historical attempts
- **FR-020**: System MUST validate all required fields (question text, minimum 2 answers, exactly 1 correct answer) before saving

**Exam/Test Session (Candidate)**

- **FR-021**: Candidate MUST be able to select a project from list of active (non-archived) projects
- **FR-022**: Candidate MUST be able to choose session mode: Test (immediate feedback) or Exam (deferred review)
- **FR-023**: Candidate MUST be able to select difficulty level per session: Easy (2 min/question), Medium (1 min/question), Hard (30 sec/question), Expert (10 sec/question)
- **FR-024**: Candidate MUST be able to specify number of questions for the session (1 to total available questions in project)
- **FR-025**: System MUST randomly select the specified number of unique questions from the project without repeats within the same session
- **FR-026**: System MUST display one question at a time with linear navigation (Next button only, no back navigation)
- **FR-027**: System MUST display countdown timer for current question based on selected difficulty level
- **FR-028**: System MUST auto-advance to next question when timer reaches 0, marking current question as unanswered
- **FR-029**: System MUST disable answer selection after timer expires or answer is submitted
- **FR-030**: Candidate MUST see Cancel button on all questions to abandon attempt at any time
- **FR-031**: System MUST confirm cancellation with dialog "Are you sure? Your progress will not be saved."

**Test Mode Behavior**

- **FR-032**: In Test mode, system MUST immediately highlight correct answer in green after candidate selects any answer
- **FR-033**: In Test mode, system MUST mark candidate's selected answer as incorrect (red) if it doesn't match correct answer
- **FR-034**: In Test mode, system MUST display Next button after answer is revealed (no Submit button)
- **FR-035**: In Test mode, system MUST allow candidate to proceed to next question at their own pace (no forced advancement)
- **FR-036**: In Test mode, system MUST display final results summary after last question with score and per-question breakdown

**Exam Mode Behavior**

- **FR-037**: In Exam mode, system MUST NOT reveal correct answers until all questions are answered or skipped
- **FR-038**: In Exam mode, system MUST display Submit button only after candidate has attempted all questions
- **FR-039**: In Exam mode, after Submit, system MUST enter review phase where each question is displayed for half the original timer duration (e.g., Hard = 15 sec review)
- **FR-040**: In Exam mode review phase, system MUST show candidate's selected answer and correct answer side-by-side with correctness indicator
- **FR-041**: In Exam mode review phase, system MUST disable answer selection (read-only review)
- **FR-042**: In Exam mode, system MUST auto-advance through review phase when review timer expires for each question
- **FR-043**: In Exam mode, system MUST display final results summary after review phase completion with score and per-question breakdown

**Results & Scoring**

- **FR-044**: System MUST calculate score as (correct answers / total questions attempted) × 100, rounded to 1 decimal place
- **FR-045**: System MUST display results summary with: total score, number of correct answers, number of questions attempted, total time spent, mode, difficulty level
- **FR-046**: System MUST display per-question breakdown showing: question number, question text, candidate's selected answer, correct answer, time spent, correctness indicator (✓/✗)
- **FR-047**: System MUST save attempt data to history immediately upon completion (not on cancel)
- **FR-048**: Attempt history record MUST include: candidate ID, project ID, date/time, mode, difficulty, questions attempted (with IDs), selected answers, correct answers, score, time per question

**Dashboard & History**

- **FR-049**: Candidate MUST be able to access personal dashboard showing all past attempts in reverse chronological order (newest first)
- **FR-050**: Candidate dashboard MUST display per attempt: date/time, project name, mode, difficulty, score, number of questions
- **FR-051**: Candidate MUST be able to click on any attempt to view detailed per-question breakdown
- **FR-052**: Candidate MUST be able to download attempt details in CSV format with columns: question_number, question_text, selected_answer, correct_answer, time_spent_seconds, is_correct
- **FR-053**: Candidate MUST be able to download attempt details in PDF format with formatted report including summary section and per-question table
- **FR-054**: Admin MUST be able to access aggregated results dashboard showing all candidate attempts across all projects
- **FR-055**: Admin dashboard MUST support filtering by: project, date range (start/end), candidate email
- **FR-056**: Admin dashboard MUST display aggregated statistics: total attempts, average score, completion rate, per-question statistics (% correct, avg time)
- **FR-057**: Admin MUST be able to download filtered results as CSV report with all attempt records

**Validation & Error Handling**

- **FR-058**: System MUST validate PDF files are valid PDF format (magic bytes check) before parsing
- **FR-059**: System MUST reject PDF uploads larger than 10MB with error message
- **FR-060**: System MUST display actionable error messages for PDF parsing failures: "Line 15: Missing correct answer marker. Expected [A], [B], [C], or [D]."
- **FR-061**: System MUST validate email format (RFC 5322 compliance) during registration
- **FR-062**: System MUST enforce password minimum requirements: 8 characters, 1 uppercase, 1 lowercase, 1 number
- **FR-063**: System MUST validate timer boundaries: Easy = 120 sec, Medium = 60 sec, Hard = 30 sec, Expert = 10 sec (no custom durations)
- **FR-064**: System MUST prevent exam start if selected question count exceeds available questions with error: "Only X questions available. Please select up to X."
- **FR-065**: System MUST display success notifications for: project created, question uploaded, exam completed, results downloaded

### Key Entities

- **User**: Represents both Admin and Candidate users. Key attributes: email (unique), hashed password, role (Admin/Candidate), registration date, last login timestamp
- **Project**: Represents a collection of questions for a specific topic/exam. Key attributes: name, description, created by (admin ID), created date, last modified date, archived status
- **Question**: Represents a single exam question. Key attributes: question text, project ID, answer options (array of 2-6 strings), correct answer index, optional explanation, created date, last modified date
- **Attempt**: Represents a single exam/test session. Key attributes: candidate ID, project ID, start timestamp, end timestamp, mode (Test/Exam), difficulty (Easy/Medium/Hard/Expert), question IDs (array), selected answers (array), score, time per question (array)
- **Answer_Selection**: Represents candidate's answer for a specific question in an attempt. Key attributes: attempt ID, question ID, selected answer index, time spent seconds, is correct boolean, timestamp

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Candidates can complete a 20-question exam in Hard mode (30 sec per question) from login to result display in under 12 minutes total (includes navigation time)
- **SC-002**: System successfully parses 95% of properly formatted PDF files containing 50 Q&A pairs within 3 seconds
- **SC-003**: Admin can create a new project and upload a 30-question PDF in under 2 minutes including validation and duplicate detection
- **SC-004**: Candidate dashboard loads and displays 100 historical attempts with full details in under 2 seconds
- **SC-005**: System maintains consistent performance with 100 concurrent active exam sessions without response time degradation beyond 500ms for answer submissions
- **SC-006**: Mobile users on smartphones (320px-428px viewport width) can complete all candidate-facing workflows (exam taking, result viewing, history browsing) without horizontal scrolling or interface obstruction
- **SC-007**: Tablet users (768px-1024px viewport) can complete all admin workflows (project creation, question management, PDF upload) without loss of functionality compared to desktop
- **SC-008**: 90% of candidates successfully complete their first exam attempt without encountering errors or requiring support assistance
- **SC-009**: Attempt history records are 100% accurate with no data loss: every completed attempt has matching question IDs, selected answers, and timestamps
- **SC-010**: Zero unauthorized access incidents: candidates cannot access other candidates' data or admin functions, admins cannot access candidate passwords

## Assumptions

- PDF question format follows a consistent structure with question text followed by lettered answer options (A, B, C, D) and a correct answer indicator. The system will document required PDF format in admin help documentation.
- Candidates have stable internet connectivity during exams. Short disconnections (<30 seconds) will auto-resume; longer disconnections will require restarting the attempt.
- Questions are primarily multiple-choice with single correct answers. True/False, multi-select, or free-text questions are out of scope for initial version.
- Admin manually reviews question bank quality. The system does not validate question content quality, only format and structure.
- Exam content is in English. Internationalization (i18n) and multi-language support are deferred to future versions.
- Result downloadability assumes candidates/admins have local file system access. No cloud storage integration (Dropbox, Google Drive) is provided initially.
- Authentication is email/password based. Social login (Google, Microsoft) and SSO enterprise integrations are deferred to future versions.
- AWS Lambda execution limits (<15 min) are sufficient for all operations. PDF parsing is optimized for files up to 200 questions.

## Out of Scope

The following features are explicitly excluded from this specification and will be addressed in future iterations:

- Real-time proctoring or anti-cheating mechanisms (webcam monitoring, tab switching detection)
- Question types beyond multiple-choice (essay questions, code submissions, drag-and-drop)
- Adaptive difficulty (system adjusting question difficulty based on candidate performance mid-exam)
- Team/group exam sessions or collaborative features
- Gamification (badges, leaderboards, achievements)
- Social features (candidate profiles, discussion forums, question comments)
- Advanced analytics (ML-powered insights, predictive scoring, question recommendation engine)
- Integration with external Learning Management Systems (LMS) like Moodle, Canvas, Blackboard
- White-labeling or multi-tenancy for different organizations
- Offline exam mode (Progressive Web App with local storage)
- Question versioning and rollback (admins editing questions creates new version, old attempts reference old versions)
- Bulk import/export of questions in formats other than PDF (JSON, CSV, DOCX)

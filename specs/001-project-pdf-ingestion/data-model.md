# Data Model: Project PDF Question Ingestion

## Entity: Project
- Purpose: Logical assessment container created by admins.
- Fields:
  - `project_id` (string, PK, immutable)
  - `title` (string, required, 3-120 chars)
  - `description` (string, optional, max 1000 chars)
  - `status` (enum: `DRAFT|PROCESSING|PUBLISHED|FAILED|ARCHIVED`)
  - `is_active` (boolean)
  - `created_by` (string, admin user id)
  - `created_at` (datetime ISO8601)
  - `updated_at` (datetime ISO8601)
  - `published_at` (datetime ISO8601, nullable)
- Validation Rules:
  - Title required and unique within active projects.
  - `PUBLISHED` requires at least one valid linked `QuestionItem`.
- Relationships:
  - 1:N with `ProjectDocument`
  - 1:N with `QuestionItem`
  - 1:N with `StudentSession`

## Entity: ProjectDocument
- Purpose: Uploaded PDF source and ingestion status tracking.
- Fields:
  - `document_id` (string, PK)
  - `project_id` (string, FK -> Project)
  - `s3_key` (string, required)
  - `file_name` (string, required)
  - `content_type` (string, must be `application/pdf`)
  - `file_size_bytes` (number, required)
  - `ingestion_status` (enum: `UPLOADED|PROCESSING|COMPLETED|FAILED`)
  - `error_message` (string, nullable)
  - `uploaded_by` (string, admin user id)
  - `uploaded_at` (datetime ISO8601)
  - `processed_at` (datetime ISO8601, nullable)
- Validation Rules:
  - Max file size enforced by configuration.
  - `COMPLETED` requires parser output with >=1 valid `QuestionItem`.
- Relationships:
  - N:1 with `Project`

## Entity: QuestionItem
- Purpose: Normalized parsed question associated with one project.
- Fields:
  - `question_id` (string, PK)
  - `project_id` (string, FK -> Project)
  - `sequence` (number, required, positive)
  - `question_type` (enum: existing supported exam types)
  - `prompt` (string, required)
  - `options` (array, optional by type)
  - `metadata` (object, optional parser/source info)
  - `is_valid` (boolean, default true)
  - `created_at` (datetime ISO8601)
- Validation Rules:
  - Sequence unique per project.
  - Prompt required and non-empty after normalization.
- Relationships:
  - N:1 with `Project`
  - 1:1 with `AnswerKey`

## Entity: AnswerKey
- Purpose: Canonical correct answer representation for scoring.
- Fields:
  - `answer_key_id` (string, PK)
  - `question_id` (string, FK -> QuestionItem, unique)
  - `project_id` (string, denormalized for query)
  - `correct_answer` (object/string/array, type-dependent)
  - `grading_mode` (enum: `EXACT|PARTIAL|ORDERED`)
  - `created_at` (datetime ISO8601)
- Validation Rules:
  - Must conform to `question_type` schema.
  - Exactly one answer key per question.
- Relationships:
  - 1:1 with `QuestionItem`

## Entity: StudentSession
- Purpose: Student test/exam attempt bound to selected project.
- Fields:
  - `session_id` (string, PK)
  - `student_id` (string, required)
  - `project_id` (string, FK -> Project)
  - `mode` (enum: `TEST|EXAM`)
  - `status` (enum: `STARTED|SUBMITTED|ABANDONED|EXPIRED`)
  - `question_ids` (array[string], immutable once started)
  - `started_at` (datetime ISO8601)
  - `submitted_at` (datetime ISO8601, nullable)
  - `score` (number, nullable)
- Validation Rules:
  - Session creation requires project in `PUBLISHED` and `is_active=true`.
  - `question_ids` must all belong to selected `project_id`.
- Relationships:
  - N:1 with `Project`

## State Transitions

### Project
- `DRAFT -> PROCESSING` on PDF upload accepted.
- `PROCESSING -> PUBLISHED` when parse persists >=1 valid Q/A pair.
- `PROCESSING -> FAILED` when parse/validation fails.
- `FAILED -> PROCESSING` on re-upload retry.
- `PUBLISHED -> ARCHIVED` when admin retires project.

### ProjectDocument
- `UPLOADED -> PROCESSING -> COMPLETED|FAILED`

### StudentSession
- `STARTED -> SUBMITTED|ABANDONED|EXPIRED`

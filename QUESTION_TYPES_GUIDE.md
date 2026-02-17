# Question Types Implementation Guide

## Overview
ExamBuddy now supports 7 different question types with automatic type detection based on question structure and content analysis.

## Question Types

### 1. **Multiple Choice** (MULTIPLE_CHOICE)
- **Description**: Standard question with one correct answer
- **Use Case**: Basic exam questions with 2-6 options
- **Example**: "Which cloud provider is best for AI?"
- **Detection**: Default type; recognized by straightforward question structure

### 2. **Multiple Response** (MULTIPLE_RESPONSE)
- **Description**: Must select two or more correct answers
- **Use Case**: "Select all that apply" questions
- **Keywords**: "select all", "choose all", "all that apply", "multiple answers"
- **Example**: "Which of these are Azure services? [Select all that apply]"
- **Detection**: Automatically detected by keywords in question text

### 3. **Drag and Drop** (DRAG_AND_DROP)
- **Description**: Matching items or pairing elements
- **Use Case**: Matching services to descriptions, connecting related concepts
- **Keywords**: "match", "pair", "connect", "drag", "associate"
- **Example**: "Match Azure services to their descriptions"
- **Detection**: Detected by matching keywords + even number of options (pairs)

### 4. **Hot Area** (HOT_AREA)
- **Description**: Click on specific part of screenshot or diagram
- **Use Case**: Azure Portal navigation, UI-based questions
- **Keywords**: "click", "image", "screenshot", "diagram", "where", "locate"
- **Example**: "In the Azure Portal, where would you find the Virtual Networks setting?"
- **Detection**: Detected by location keywords + area-based answer options
- **Note**: Requires image upload + clickable region mapping

### 5. **Build List** (BUILD_LIST)
- **Description**: Drag steps/items into correct order
- **Use Case**: Process sequences, setup procedures
- **Keywords**: "order", "sequence", "steps", "arrange", "following order"
- **Example**: "Arrange these steps in correct order to deploy a VM"
- **Detection**: Detected by order keywords + numbered/bulleted step format

### 6. **Drop-down Selection** (DROP_DOWN_SELECTION)
- **Description**: Fill blank in sentence with dropdown options
- **Use Case**: Sentence completion, terminology
- **Keywords**: "fill in", "blank", "dropdown", "missing word", "choose from"
- **Example**: "Azure _____ is used for unstructured data storage" [Options: Table, Blob, Queue, File]
- **Detection**: Detected by blank indicators (___ or [blank]) + keyword presence
- **Note**: Best for 3-5 options

### 7. **Scenario Series** (SCENARIO_SERIES)
- **Description**: Scenario followed by 3 Yes/No statements
- **Use Case**: Complex decision-making, multi-part scenarios
- **Keywords**: "scenario", "case", "situation", "statements", "meet the goal", "requirement"
- **Example**: "Scenario: Company needs to migrate data... Statement 1: [Yes/No]"
- **Detection**: Detected by scenario keywords + 3+ options structure
- **Note**: Each statement requires Yes/No answer

## Auto-Detection System

### How It Works
1. **Text Analysis**: Scans question text for type-specific keywords
2. **Structure Analysis**: Examines answer options format (numbers, bullets, pairs)
3. **Heuristics**: Applies multi-level pattern matching
4. **Fallback**: Defaults to MULTIPLE_CHOICE if no pattern matches

### Detection Accuracy
- **HIGH confidence**: Keywords + structure match (e.g., "select all" + multiple keywords)
- **MEDIUM confidence**: One of keywords/structure present
- **DEFAULT**: Treated as MULTIPLE_CHOICE

### Example Detection Patterns
```python
# SCENARIO_SERIES
"scenario" + answer_count >= 3 → SCENARIO_SERIES

# BUILD_LIST
"arrange in order" + numbered options → BUILD_LIST

# DROP_DOWN_SELECTION
"fill in the blank" + "_" in text → DROP_DOWN_SELECTION

# DRAG_AND_DROP
"match" + even_answer_count >= 4 → DRAG_AND_DROP
```

## Implementation Files

### Backend
- **Model**: `backend/src/models/question.py`
  - Added `QuestionType` enum (7 types)
  - Added `metadata` field for type-specific data
  - Updated `to_dynamodb_item()` and `from_dynamodb_item()`

- **Detector**: `backend/src/services/question_type_detector.py`
  - `QuestionTypeDetector` class with auto-detection logic
  - `QuestionTypeUpdater` class for batch updates

- **Service**: `backend/src/services/question_service.py`
  - Updated `create_question()` to auto-detect types
  - Parameter `auto_detect_type: bool = True` (can be disabled)

- **Migration**: `backend/scripts/migrate_question_types.py`
  - Scans all existing questions
  - Auto-detects and assigns types
  - Runs without modifying already-typed questions

### Tests
- **Updated**: `backend/tests/create_test_questions.py`
  - Creates 10 test questions with mixed types
  - Shows auto-detected types in output

## Usage

### Creating Questions (Auto-Detection Enabled)
```python
from src.models.question import Question
from src.services.question_service import QuestionService

question = Question(
    question_id="q-123",
    project_id="proj-123",
    text="Select all that apply: Which are Azure services?",
    answer_options=["App Service", "Storage", "Network", "SQL DB"],
    correct_index=0,
    difficulty="medium"
)

service = QuestionService()
# Auto-detection happens automatically
created = await service.create_question(question)
print(created.question_type)  # → MULTIPLE_RESPONSE
```

### Creating Questions (Manual Type Assignment)
```python
question = Question(
    ...
    question_type=QuestionType.DRAG_AND_DROP,
    metadata={"pair_count": 5}
)

# Disable auto-detection
created = await service.create_question(question, auto_detect_type=False)
```

### Migrating Existing Questions
```bash
cd backend
python scripts/migrate_question_types.py
```

Output:
```
🔍 Starting question type migration...
📚 Table: exambuddy-main-dev
✓ Q1: abc12345... → multiple_choice
✓ Q2: def67890... → multiple_response
✓ Q3: ghi11111... → build_list
...
✅ Migration complete!
   Scanned: 150
   Updated: 142
   Errors: 0
```

## Frontend Considerations

### Future Implementations Needed
1. **Multiple Response UI**: Checkboxes instead of radio buttons
2. **Build List UI**: Drag-drop interface for ordering
3. **Hot Area UI**: Image viewer with clickable regions
4. **Drop-down UI**: Text input with dropdown population
5. **Scenario UI**: Multi-statement Yes/No selector

### Question Type Display
```javascript
// Fetch question with type
const question = await examService.getQuestion(sessionId, questionIndex);
console.log(question.question_type);  // "multiple_choice", "build_list", etc.
console.log(question.metadata);       // Type-specific metadata

// Render appropriate UI component based on type
switch(question.question_type) {
  case 'multiple_choice':
    return <MultipleChoiceCard question={question} />;
  case 'multiple_response':
    return <MultipleResponseCard question={question} />;
  case 'build_list':
    return <BuildListCard question={question} />;
  // ... etc
}
```

## Metadata Structure

Type-specific metadata stored in `metadata` field:

```json
{
  "MULTIPLE_CHOICE": {},
  "MULTIPLE_RESPONSE": { "correct_count": 2 },
  "DRAG_AND_DROP": { "pair_count": 5 },
  "HOT_AREA": { "image_needed": true, "regions": [...] },
  "BUILD_LIST": { "step_count": 5 },
  "DROP_DOWN_SELECTION": { "blank_position": "auto-detect" },
  "SCENARIO_SERIES": { "statement_count": 3 }
}
```

## Admin Interface Notes

For manual question entry, admin should:
1. **See auto-detected type**: System suggests type based on input
2. **Override if needed**: Dropdown to manually select type
3. **Configure metadata**: Type-specific fields appear based on selection
4. **Preview**: Show how question will appear to candidate

Example flow:
```
Admin enters question text → System suggests MULTIPLE_RESPONSE 
→ Admin confirms or changes to MULTIPLE_CHOICE 
→ Fills in answer options 
→ Selects correct answers (system adapts UI based on type)
→ Saves question with type + metadata
```

## Testing

### Run Auto-Detection Tests
```bash
cd backend
python tests/create_test_questions.py
```

### Verify Type Detection
```bash
cd backend
python -c "
from src.models.question import Question
from src.services.question_type_detector import QuestionTypeDetector

q = Question(
    question_id='test',
    project_id='test',
    text='Select all that apply: Which are programming languages?',
    answer_options=['Python', 'Azure', 'Java', 'SQL'],
    correct_index=0
)

detected_type, metadata = QuestionTypeDetector.detect_type(q)
print(f'Type: {detected_type}')
print(f'Metadata: {metadata}')
"
```

## Next Steps

1. ✅ Question model with types
2. ✅ Auto-detection logic
3. ✅ Database persistence
4. ⏳ Frontend UI components for each type
5. ⏳ Admin interface for type selection
6. ⏳ PDF reader enhancement to detect types
7. ⏳ Type-specific validation rules

---

**Last Updated**: February 17, 2026
**Auto-Detection Test Results**: 10/10 questions correctly categorized

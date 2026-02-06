# DynamoDB Single-Table Design for ExamBuddy

**Date:** February 6, 2026  
**Purpose:** Schema design and access pattern analysis for ExamBuddy exam management platform

---

## Executive Summary

**Recommendation: Hybrid Approach with Single-Table Core**

After analyzing the access patterns and entity relationships, I recommend a **primarily single-table design** with the following characteristics:
- Core operational entities (User, Project, Question, Attempt, AnswerSelection) in one table
- Leverage DynamoDB's partition key + sort key model with GSIs for access patterns
- Use composite keys and well-designed GSIs to handle all required queries efficiently

---

## Entity Relationships

```
User (Admin) 
  └── 1:N → Project
              └── 1:N → Question

User (Candidate)
  └── 1:N → Attempt
              └── 1:N → AnswerSelection
                          └── N:1 → Question (reference)
```

---

## Single-Table Design

### Table Name: `ExamBuddyTable`

#### Primary Key Structure

| Entity Type      | PK (Partition Key)        | SK (Sort Key)              |
|------------------|---------------------------|----------------------------|
| User             | `USER#<email>`            | `USER#<email>`             |
| Project          | `ADMIN#<admin_id>`        | `PROJECT#<project_id>`     |
| Question         | `PROJECT#<project_id>`    | `QUESTION#<question_id>`   |
| Attempt          | `CANDIDATE#<candidate_id>`| `ATTEMPT#<attempt_id>`     |
| AnswerSelection  | `ATTEMPT#<attempt_id>`    | `ANSWER#<answer_id>`       |

#### Global Secondary Indexes (GSIs)

**GSI1: Entity Lookup Index**
- **Purpose:** Direct entity access by ID, project metadata queries
- **PK:** `GSI1PK` = `<EntityType>#<entity_id>` 
- **SK:** `GSI1SK` = `<EntityType>#<entity_id>` or metadata sort key
- **Projection:** ALL

**GSI2: Time-Series and Filter Index**
- **Purpose:** Date-range queries, status filtering, admin analytics
- **PK:** `GSI2PK` = `PROJECT#<project_id>` (for attempts) or `ADMIN#<admin_id>` (for projects)
- **SK:** `GSI2SK` = `<timestamp>#<entity_id>` or `STATUS#<status>#<timestamp>`
- **Projection:** ALL

**GSI3: Status Filter Index**
- **Purpose:** Filter projects by archived status, list active/inactive entities
- **PK:** `GSI3PK` = `ADMIN#<admin_id>#STATUS#<archived>`
- **SK:** `GSI3SK` = `PROJECT#<project_id>`
- **Projection:** ALL

---

## Sample Item Structures

### User Item

```json
{
  "PK": "USER#admin@example.com",
  "SK": "USER#admin@example.com",
  "GSI1PK": "USER#user-uuid-123",
  "GSI1SK": "USER#user-uuid-123",
  "EntityType": "USER",
  "user_id": "user-uuid-123",
  "email": "admin@example.com",
  "name": "John Doe",
  "role": "ADMIN",
  "created_at": "2026-02-06T10:00:00Z",
  "updated_at": "2026-02-06T10:00:00Z"
}
```

### Project Item

```json
{
  "PK": "ADMIN#user-uuid-123",
  "SK": "PROJECT#proj-uuid-456",
  "GSI1PK": "PROJECT#proj-uuid-456",
  "GSI1SK": "PROJECT#proj-uuid-456",
  "GSI2PK": "ADMIN#user-uuid-123",
  "GSI2SK": "2026-02-06T10:00:00Z#proj-uuid-456",
  "GSI3PK": "ADMIN#user-uuid-123#STATUS#false",
  "GSI3SK": "PROJECT#proj-uuid-456",
  "EntityType": "PROJECT",
  "project_id": "proj-uuid-456",
  "admin_id": "user-uuid-123",
  "title": "AWS Certification Exam",
  "description": "Practice questions for AWS Solutions Architect",
  "archived": false,
  "question_count": 50,
  "created_at": "2026-02-06T10:00:00Z",
  "updated_at": "2026-02-06T10:00:00Z"
}
```

### Question Item

```json
{
  "PK": "PROJECT#proj-uuid-456",
  "SK": "QUESTION#quest-uuid-789",
  "GSI1PK": "QUESTION#quest-uuid-789",
  "GSI1SK": "QUESTION#quest-uuid-789",
  "EntityType": "QUESTION",
  "question_id": "quest-uuid-789",
  "project_id": "proj-uuid-456",
  "question_text": "What is Amazon S3?",
  "question_type": "multiple_choice",
  "options": ["A", "B", "C", "D"],
  "correct_answer": "C",
  "explanation": "Amazon S3 is object storage...",
  "order": 1,
  "created_at": "2026-02-06T10:00:00Z"
}
```

### Attempt Item

```json
{
  "PK": "CANDIDATE#user-uuid-999",
  "SK": "ATTEMPT#attempt-uuid-111",
  "GSI1PK": "ATTEMPT#attempt-uuid-111",
  "GSI1SK": "ATTEMPT#attempt-uuid-111",
  "GSI2PK": "PROJECT#proj-uuid-456",
  "GSI2SK": "2026-02-06T14:30:00Z#attempt-uuid-111",
  "EntityType": "ATTEMPT",
  "attempt_id": "attempt-uuid-111",
  "candidate_id": "user-uuid-999",
  "project_id": "proj-uuid-456",
  "started_at": "2026-02-06T14:30:00Z",
  "completed_at": "2026-02-06T15:45:00Z",
  "status": "COMPLETED",
  "score": 42,
  "total_questions": 50,
  "time_taken_seconds": 4500
}
```

### AnswerSelection Item

```json
{
  "PK": "ATTEMPT#attempt-uuid-111",
  "SK": "ANSWER#quest-uuid-789",
  "GSI1PK": "ANSWER#answer-uuid-222",
  "GSI1SK": "ANSWER#answer-uuid-222",
  "EntityType": "ANSWER",
  "answer_id": "answer-uuid-222",
  "attempt_id": "attempt-uuid-111",
  "question_id": "quest-uuid-789",
  "selected_answer": "C",
  "is_correct": true,
  "answered_at": "2026-02-06T14:35:00Z"
}
```

---

## Query Patterns with Pseudocode

### 1. Get User by Email (Login)

**Access Pattern:** Direct lookup by email  
**Table/Index:** Base Table  
**Operation:** GetItem

```python
# Pseudocode
response = dynamodb.get_item(
    TableName='ExamBuddyTable',
    Key={
        'PK': 'USER#admin@example.com',
        'SK': 'USER#admin@example.com'
    }
)
user = response['Item']
```

**Complexity:** O(1) - Single item read  
**Cost:** 1 RCU (or 0.5 RCU for eventually consistent)

---

### 2. List Projects by Admin ID

**Access Pattern:** Get all projects for an admin  
**Table/Index:** Base Table  
**Operation:** Query

```python
# Pseudocode
response = dynamodb.query(
    TableName='ExamBuddyTable',
    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
    ExpressionAttributeValues={
        ':pk': 'ADMIN#user-uuid-123',
        ':sk_prefix': 'PROJECT#'
    }
)
projects = response['Items']
```

**Complexity:** O(n) where n = number of projects for admin  
**Cost:** Depends on item size, typically 1 RCU per 4KB

---

### 3. List Questions by Project ID

**Access Pattern:** Get all questions for a project  
**Table/Index:** Base Table  
**Operation:** Query

```python
# Pseudocode
response = dynamodb.query(
    TableName='ExamBuddyTable',
    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
    ExpressionAttributeValues={
        ':pk': 'PROJECT#proj-uuid-456',
        ':sk_prefix': 'QUESTION#'
    }
)
questions = response['Items']
```

**Complexity:** O(n) where n = number of questions in project  
**Cost:** Depends on item size and pagination

---

### 4. List Attempts by Candidate ID

**Access Pattern:** Get all exam attempts for a candidate  
**Table/Index:** Base Table  
**Operation:** Query

```python
# Pseudocode
response = dynamodb.query(
    TableName='ExamBuddyTable',
    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
    ExpressionAttributeValues={
        ':pk': 'CANDIDATE#user-uuid-999',
        ':sk_prefix': 'ATTEMPT#'
    },
    ScanIndexForward=False  # Most recent first
)
attempts = response['Items']
```

**Complexity:** O(n) where n = number of attempts  
**Cost:** 1 RCU per 4KB

---

### 5. List Answer Selections by Attempt ID

**Access Pattern:** Get all answers for an attempt  
**Table/Index:** Base Table  
**Operation:** Query

```python
# Pseudocode
response = dynamodb.query(
    TableName='ExamBuddyTable',
    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
    ExpressionAttributeValues={
        ':pk': 'ATTEMPT#attempt-uuid-111',
        ':sk_prefix': 'ANSWER#'
    }
)
answers = response['Items']
```

**Complexity:** O(n) where n = number of questions answered  
**Cost:** Minimal, typically 1-2 RCUs for standard exam

---

### 6. Get Project with Question Count

**Approach 1:** Store question_count as attribute (Recommended)

```python
# Pseudocode - Direct lookup
response = dynamodb.get_item(
    TableName='ExamBuddyTable',
    Key={
        'PK': 'ADMIN#user-uuid-123',
        'SK': 'PROJECT#proj-uuid-456'
    }
)
project = response['Item']
question_count = project['question_count']
```

**Note:** Update `question_count` atomically when adding/removing questions:

```python
# When adding a question
dynamodb.update_item(
    TableName='ExamBuddyTable',
    Key={
        'PK': 'ADMIN#user-uuid-123',
        'SK': 'PROJECT#proj-uuid-456'
    },
    UpdateExpression='SET question_count = question_count + :inc',
    ExpressionAttributeValues={
        ':inc': 1
    }
)
```

**Approach 2:** Query + count (Not recommended for frequent access)

```python
# Pseudocode - Less efficient
response = dynamodb.query(
    TableName='ExamBuddyTable',
    KeyConditionExpression='PK = :pk AND begins_with(SK, :sk_prefix)',
    ExpressionAttributeValues={
        ':pk': 'PROJECT#proj-uuid-456',
        ':sk_prefix': 'QUESTION#'
    },
    Select='COUNT'
)
question_count = response['Count']
```

---

### 7. Filter Projects by Archived Status

**Access Pattern:** List all projects for admin filtered by archived status  
**Table/Index:** GSI3  
**Operation:** Query

```python
# Pseudocode - Get non-archived projects
response = dynamodb.query(
    TableName='ExamBuddyTable',
    IndexName='GSI3',
    KeyConditionExpression='GSI3PK = :pk',
    ExpressionAttributeValues={
        ':pk': 'ADMIN#user-uuid-123#STATUS#false'
    }
)
active_projects = response['Items']

# Get archived projects
response = dynamodb.query(
    TableName='ExamBuddyTable',
    IndexName='GSI3',
    KeyConditionExpression='GSI3PK = :pk',
    ExpressionAttributeValues={
        ':pk': 'ADMIN#user-uuid-123#STATUS#true'
    }
)
archived_projects = response['Items']
```

**Complexity:** O(n) where n = projects matching status  
**Cost:** GSI query cost (same as base table)

---

### 8. Admin: List All Attempts with Filters

**Use Case:** Admin wants to see all attempts for a specific project within a date range

**Access Pattern:** Query attempts by project with date filtering  
**Table/Index:** GSI2  
**Operation:** Query with KeyCondition

```python
# Pseudocode - Attempts for project in date range
response = dynamodb.query(
    TableName='ExamBuddyTable',
    IndexName='GSI2',
    KeyConditionExpression='GSI2PK = :pk AND GSI2SK BETWEEN :start_date AND :end_date',
    FilterExpression='EntityType = :entity_type',
    ExpressionAttributeValues={
        ':pk': 'PROJECT#proj-uuid-456',
        ':start_date': '2026-02-01T00:00:00Z#',
        ':end_date': '2026-02-28T23:59:59Z#',
        ':entity_type': 'ATTEMPT'
    }
)
attempts = response['Items']
```

**For Multiple Projects (Admin Dashboard):**

```python
# Pseudocode - Requires multiple queries or BatchGetItem
project_ids = ['proj-uuid-456', 'proj-uuid-789']
all_attempts = []

for project_id in project_ids:
    response = dynamodb.query(
        TableName='ExamBuddyTable',
        IndexName='GSI2',
        KeyConditionExpression='GSI2PK = :pk AND GSI2SK BETWEEN :start_date AND :end_date',
        ExpressionAttributeValues={
            ':pk': f'PROJECT#{project_id}',
            ':start_date': '2026-02-01T00:00:00Z#',
            ':end_date': '2026-02-28T23:59:59Z#'
        }
    )
    all_attempts.extend(response['Items'])
```

**Complexity:** O(p * n) where p = projects, n = attempts per project  
**Limitation:** Not ideal for cross-project analytics at scale

---

## GSI Design Summary

### GSI1: Entity Lookup Index
- **Keys:** `GSI1PK` = `<EntityType>#<entity_id>`, `GSI1SK` = same
- **Use Cases:**
  - Direct entity lookup by ID (without knowing parent)
  - Get project details by project_id
  - Get attempt details by attempt_id
- **Projection:** ALL (enables read without base table lookup)

### GSI2: Time-Series and Analytics Index
- **Keys:** `GSI2PK` = context-dependent, `GSI2SK` = timestamp-based
- **Use Cases:**
  - Date range queries for attempts by project
  - Time-based sorting and filtering
  - Admin analytics queries
- **Projection:** ALL
- **Note:** Date format in SK enables efficient range queries

### GSI3: Status Filter Index
- **Keys:** `GSI3PK` = `ADMIN#<id>#STATUS#<bool>`, `GSI3SK` = entity key
- **Use Cases:**
  - Filter projects by archived status
  - List active vs inactive entities
- **Projection:** ALL
- **Alternative:** Could use sparse index (only indexed when archived=true)

---

## Pros and Cons Analysis

### Single-Table Design Pros ✅

1. **Cost Efficiency**
   - Single provisioned capacity pool (if using provisioned mode)
   - Fewer tables = lower base costs
   - Reduced complexity in capacity planning

2. **Atomic Operations**
   - TransactWriteItems can span entities in same table
   - Example: Create attempt + multiple answer selections atomically

3. **Simplified Backup/Restore**
   - Single table to backup
   - Point-in-time recovery for all entities

4. **Better Partition Distribution**
   - Related data can be queried together efficiently
   - Hot partitions less likely with well-designed keys

5. **Reduced Connection Overhead**
   - Single table = fewer connections, simpler code

### Single-Table Design Cons ❌

1. **Schema Complexity**
   - Requires careful key design upfront
   - Harder to modify access patterns later
   - Developer learning curve

2. **Overloaded Indexes**
   - GSIs serve multiple purposes
   - Less intuitive than dedicated tables

3. **Item Size Limits**
   - 400KB limit per item (unlikely to hit with this design)
   - Large questions with embedded media might need S3 references

4. **Analytics Limitations**
   - Cross-partition queries expensive
   - "List all attempts across all projects" requires multiple queries or scan
   - May need to export to data warehouse for complex analytics

5. **Type Safety**
   - Single table = mixed entity types
   - Application must handle type discrimination

---

### Multi-Table Design Pros ✅

1. **Intuitive Schema**
   - Each table represents clear entity
   - Easier for developers to understand

2. **Independent Scaling**
   - Scale each table independently
   - Different capacity modes per table

3. **Simpler Access Patterns**
   - Direct queries without complex key logic
   - Standard relational-like patterns

4. **Type Safety**
   - Each table has consistent schema
   - Easier validation and typing

### Multi-Table Design Cons ❌

1. **Higher Costs**
   - Multiple provisioned capacity pools
   - More tables = higher minimum costs

2. **No Cross-Table Transactions**
   - Cannot atomically write across tables
   - Need application-level coordination

3. **More Complex Backup**
   - Must backup each table separately
   - Coordination for consistent snapshots

4. **Network Overhead**
   - More API calls to different tables
   - Increased latency for related data

---

## Recommendation: Single-Table with Caveats

### Best Fit Scenarios for Single-Table

✅ Use single-table design if:
- Access patterns are well-defined and stable
- Mostly 1:N relationships queried together
- Transaction atomicity is important
- Cost optimization is priority
- Team has DynamoDB expertise

### When to Consider Multi-Table

⚠️ Consider multi-table if:
- Access patterns are evolving rapidly
- Need to run ad-hoc analytics queries frequently
- Team is new to DynamoDB
- Independent scaling per entity is required
- Regulatory requirements for data separation

---

## Capacity Planning Guidance

### On-Demand vs Provisioned

#### **On-Demand Mode (Recommended for Start)**

**Advantages:**
- No capacity planning required
- Automatic scaling to handle spikes
- Pay only for what you use
- Ideal for unpredictable workloads

**Use When:**
- Traffic patterns are unknown
- Infrequent or spiky access
- Getting started / MVP phase
- Traffic < 25% of provisioned equivalent

**Pricing Model:**
- $1.25 per million write request units (WRU)
- $0.25 per million read request units (RRU)
- Storage: $0.25 per GB-month

**Example Cost (Small Scale):**
```
Monthly Usage:
- 1M logins (reads): 1M * $0.25 / 1M = $0.25
- 100K attempts (writes): 100K * $1.25 / 1M = $0.125
- 500K question fetches: 500K * $0.25 / 1M = $0.125
- Storage (5GB): 5 * $0.25 = $1.25
Total: ~$1.75/month
```

---

#### **Provisioned Mode (For Predictable Load)**

**Advantages:**
- Lower cost at scale (40-60% cheaper than on-demand)
- Predictable billing
- Reserved capacity discounts available
- Auto-scaling available

**Use When:**
- Traffic patterns are predictable
- Consistently high throughput
- Running production workload with history

**Pricing Model:**
- $0.00065 per WCU-hour (~$0.47 per WCU-month)
- $0.00013 per RCU-hour (~$0.09 per RCU-month)
- Storage: $0.25 per GB-month

**Capacity Estimation Example:**

```
Assumptions:
- 1000 active users
- 50 exams/day with 50 questions each
- Average read: 4KB, write: 2KB

Read Capacity:
- Login: 1000 users * 1 read/day = 1000 reads/day
- Questions: 50 exams * 50 questions = 2500 reads/day
- Answer fetches: 50 exams * 50 = 2500 reads/day
- Total: 6000 reads/day ≈ 0.07 reads/sec (1 RCU)

Write Capacity:
- Attempts: 50 writes/day ≈ 0.0006 writes/sec (1 WCU)
- Answers: 2500 writes/day ≈ 0.03 writes/sec (1 WCU)
- Total: 1 WCU

Monthly Cost:
- 5 RCU (with buffer): 5 * $0.09 = $0.45
- 5 WCU (with buffer): 5 * $0.47 = $2.35
- Storage (5GB): $1.25
Total: ~$4.05/month
```

**Note:** At low scale, on-demand is cheaper. Break-even typically at 25-40% sustained utilization.

---

### Scaling Strategy

**Phase 1: MVP/Launch (Months 1-6)**
- Use On-Demand mode
- Monitor CloudWatch metrics
- Establish baseline patterns

**Phase 2: Growth (Months 6-12)**
- Analyze usage patterns
- Switch to Provisioned if traffic is predictable
- Enable auto-scaling (50-80% target utilization)
- Set alarms for throttling

**Phase 3: Scale (12+ months)**
- Fine-tune provisioned capacity
- Consider reserved capacity
- Implement caching (DAX) for hot reads
- Export cold data to S3 for analytics

---

## Limitations and Edge Cases

### 1. Admin Analytics Queries

**Problem:** "Show me all attempts across all projects in the last month"

**Challenge:**
- Requires querying multiple partitions (one per project)
- Not efficient in DynamoDB
- Can hit query limits with many projects

**Solutions:**

**Option A: Application-Level Aggregation**
```python
# Query each project separately, aggregate in application
all_projects = get_admin_projects(admin_id)
all_attempts = []
for project in all_projects:
    attempts = query_attempts_by_project(
        project_id=project.id,
        start_date=start,
        end_date=end
    )
    all_attempts.extend(attempts)
```
**Limitation:** Slow with 100+ projects

**Option B: DynamoDB Streams + Aggregation Table**
- Stream changes to Lambda
- Maintain aggregation table with admin-level rollups
- Query aggregation table for analytics

**Option C: Export to Analytics Store**
- DynamoDB → Kinesis Firehose → S3
- Query with Athena for complex analytics
- Use DynamoDB for operational queries only

**Recommendation:** Use Option A for < 50 projects, Option B/C at scale

---

### 2. Hot Partitions

**Risk:** Popular projects with many concurrent attempts

**Example:**
- "AWS Cert Prep" project has 1000 concurrent users
- All attempts write to `PROJECT#popular-proj` partition in GSI2

**Mitigation:**
1. **Partition Key Suffixing**
   ```
   GSI2PK = PROJECT#proj-uuid-456#SHARD#{hash(attempt_id) % 10}
   ```
   Spreads load across 10 partitions

2. **Use On-Demand Mode**
   - Automatically handles bursts up to 40K RCU/WCU

3. **Cache Frequently Read Items**
   - Use DynamoDB Accelerator (DAX) for hot project metadata

---

### 3. Large Exams (1000+ Questions)

**Problem:** Fetching all questions for mega-exam

**Challenge:**
- Query returns max 1MB per page
- ~100-200 questions per page (5-10KB each)
- Requires pagination

**Solutions:**

**Option A: Pagination (Standard)**
```python
questions = []
last_key = None
while True:
    response = query_questions(
        project_id=proj_id,
        exclusive_start_key=last_key
    )
    questions.extend(response['Items'])
    last_key = response.get('LastEvaluatedKey')
    if not last_key:
        break
```

**Option B: Question Sets (Denormalized)**
- Store questions in batches of 50
- Single item per set (e.g., `QUESTIONSET#1`)
- Reduces query count

**Option C: S3 Hybrid**
- Store full question bank as JSON in S3
- DynamoDB holds metadata + S3 URI
- Fetch from S3 when loading exam

**Recommendation:** Option A for < 500 questions, Option C for larger

---

### 4. Eventual Consistency in GSIs

**Issue:** GSIs are eventually consistent (typically < 1 second lag)

**Edge Case:**
1. Admin creates project
2. Immediately queries GSI3 for project list
3. New project not yet visible

**Mitigation:**
1. **Read-after-write from base table**
   ```python
   # After creating project
   project = create_project(...)
   
   # Read from base table (strongly consistent)
   confirm = get_item(PK=f"ADMIN#{admin_id}", SK=f"PROJECT#{project_id}")
   ```

2. **Client-side tracking**
   - Return created item directly to client
   - Update client cache optimistically

3. **Use base table query when strong consistency needed**
   - Trade flexibility for consistency

---

### 5. Item Size Limits (400KB)

**Risk:** Questions with rich media, long explanations

**Scenario:**
- Question with embedded images (base64)
- Detailed explanation with diagrams
- Item size exceeds 400KB

**Solutions:**

**Option A: Store Media in S3**
```json
{
  "question_id": "quest-123",
  "question_text": "What is shown in the diagram?",
  "image_url": "s3://bucket/questions/quest-123.png",
  "explanation": "Long text...",
  "explanation_images": [
    "s3://bucket/explanations/quest-123-1.png"
  ]
}
```

**Option B: Compress Data**
- Use gzip compression for long text
- Store as binary attribute

**Option C: Split Large Items**
- Main question item (< 10KB)
- Separate explanation item if needed

**Recommendation:** Always use S3 for media, keep DynamoDB items < 10KB

---

### 6. Transaction Limits

**Limit:** TransactWriteItems supports max 100 items per transaction

**Edge Case:** Creating exam attempt with 150 answer selections

**Solution:**
```python
# Write attempt + first 99 answers in transaction
with_transaction([
    put_item(attempt),
    *[put_item(answer) for answer in answers[:99]]
])

# Write remaining answers without transaction
for answer in answers[99:]:
    put_item(answer)
```

**Alternative:** Lazy-write answers as user progresses through exam

---

### 7. Query Result Size Limits

**Limit:** Query returns max 1MB, then paginates

**Challenge:** Admin queries all attempts for busy project

**Impact:**
- First page: 200-300 attempts (3-4KB each)
- Requires pagination for more

**Mitigation:**
- Implement cursor-based pagination in API
- Cache recent results
- Use date range filters to reduce result size

---

## Data Consistency Patterns

### Maintaining question_count in Project

**Challenge:** Keep count accurate when questions added/removed

**Pattern: Atomic Counter Update**

```python
# When adding question
dynamodb.transact_write_items([
    {
        'Put': {
            'TableName': 'ExamBuddyTable',
            'Item': question_item
        }
    },
    {
        'Update': {
            'TableName': 'ExamBuddyTable',
            'Key': {'PK': f'ADMIN#{admin_id}', 'SK': f'PROJECT#{project_id}'},
            'UpdateExpression': 'SET question_count = question_count + :inc',
            'ExpressionAttributeValues': {':inc': 1}
        }
    }
])
```

**Benefits:**
- Guaranteed consistency
- No race conditions
- Single operation

---

## Migration and Versioning Strategy

### Schema Evolution

**Challenge:** Adding new access patterns after launch

**Strategy: Additive Changes Only**

1. **Add new GSI** (doesn't affect existing data)
2. **Backfill attributes** via scan or DynamoDB Streams
3. **Dual-write period** (write to old + new pattern)
4. **Switch read traffic** to new pattern
5. **Deprecate old pattern**

**Example:** Adding "project category" filter

```python
# Step 1: Add GSI4 for category filtering
GSI4PK = "CATEGORY#{category}"
GSI4SK = "PROJECT#{project_id}"

# Step 2: Backfill existing projects
for project in all_projects:
    update_item(
        Key=project_key,
        UpdateExpression='SET GSI4PK = :pk, GSI4SK = :sk',
        ExpressionAttributeValues={
            ':pk': f'CATEGORY#{project.category}',
            ':sk': f'PROJECT#{project.id}'
        }
    )
```

---

## Monitoring and Alarms

### Key CloudWatch Metrics

1. **ConsumedReadCapacityUnits / ConsumedWriteCapacityUnits**
   - Track actual consumption
   - Alert if exceeds 80% of provisioned

2. **ThrottledRequests**
   - Alert immediately (indicates capacity issue)
   - Should be near-zero

3. **UserErrors**
   - Track validation failures
   - Monitor for schema issues

4. **SystemErrors**
   - DynamoDB service issues
   - Rare but critical

5. **SuccessfulRequestLatency**
   - Track p50, p95, p99
   - Alert if > 50ms (p99)

### GSI-Specific Monitoring

- **OnlineIndexPercentageProgress** (during GSI creation)
- **OnlineIndexConsumedWriteCapacity** (GSI write cost)

---

## Security Considerations

### 1. Attribute-Level Encryption

```python
# Use AWS KMS for sensitive data
project_item = {
    'PK': 'ADMIN#user-123',
    'SK': 'PROJECT#proj-456',
    'title': 'AWS Cert',  # Not encrypted
    'description': encrypt_with_kms('Sensitive description'),  # Encrypted
    'admin_notes': encrypt_with_kms('Private admin notes')  # Encrypted
}
```

### 2. IAM Policies

**Principle of Least Privilege:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:Query",
        "dynamodb:GetItem"
      ],
      "Resource": "arn:aws:dynamodb:region:account:table/ExamBuddyTable",
      "Condition": {
        "ForAllValues:StringLike": {
          "dynamodb:LeadingKeys": ["USER#${aws:username}"]
        }
      }
    }
  ]
}
```

**Restricts users to query only their own items**

### 3. VPC Endpoints

- Use VPC endpoints for DynamoDB access
- Prevents traffic over public internet
- Lower latency, higher security

---

## Cost Optimization Tips

### 1. Right-Size Items

- Keep items < 4KB to minimize RCU consumption
- Move large attributes to S3

### 2. Use Eventually Consistent Reads

- 50% cheaper than strongly consistent
- Acceptable for most use cases

### 3. Batch Operations

```python
# Instead of 100 GetItem calls (100 RCUs)
for item_key in keys:
    get_item(key=item_key)

# Use BatchGetItem (25-50 RCUs depending on item size)
batch_get_item(keys=keys)
```

### 4. Sparse Indexes

- Only index items with specific attributes
- Reduces GSI storage and write costs

```python
# Only add to GSI when archived
if project.archived:
    item['GSI3PK'] = f'ADMIN#{admin_id}#ARCHIVED'
    item['GSI3SK'] = f'PROJECT#{project_id}'
```

### 5. TTL for Temporary Data

- Auto-delete old attempts after 90 days
- Free deletion (no WCU cost)

```python
import time

item['ttl'] = int(time.time()) + (90 * 24 * 60 * 60)  # 90 days
```

---

## Testing Strategy

### 1. Unit Tests

- Test key generation logic
- Validate item structure

### 2. Integration Tests

- Test each access pattern
- Verify GSI queries return expected results

### 3. Load Testing

- Use Artillery or Locust
- Simulate concurrent exam attempts
- Monitor throttling and latency

### 4. Chaos Testing

- Test throttling scenarios
- GSI backfill during production traffic
- Partition hot-key scenarios

---

## Alternative: Multi-Table Comparison

For completeness, here's what a multi-table design would look like:

### Tables

1. **Users** (PK: user_id)
2. **Projects** (PK: project_id, GSI: admin_id)
3. **Questions** (PK: question_id, GSI: project_id)
4. **Attempts** (PK: attempt_id, GSI1: candidate_id, GSI2: project_id)
5. **AnswerSelections** (PK: answer_id, GSI: attempt_id)

### Access Pattern Comparison

| Pattern | Single-Table | Multi-Table |
|---------|--------------|-------------|
| Get user by email | 1 GetItem | 1 Query on GSI |
| List projects by admin | 1 Query | 1 Query on GSI |
| List questions by project | 1 Query | 1 Query on GSI |
| Get project + questions | 2 Queries | 2 Queries |
| Create attempt + answers | 1 Transaction | N/A (can't transact) |

**Cost Comparison (Provisioned):**
- Single-Table: $4.05/month (5 RCU + 5 WCU)
- Multi-Table: $20.25/month (5 tables × 1 RCU + 1 WCU each × cost)

**Multi-table is 5x more expensive at minimum capacity**

---

## Final Recommendation Summary

### ✅ **Go with Single-Table Design**

**Reasons:**
1. Access patterns are well-defined and stable
2. Cost efficiency (5x cheaper at scale)
3. Atomic transactions across entities
4. Related data queried together (projects → questions, attempts → answers)
5. Suitable for OLTP workload

### ⚠️ **But Plan for Analytics Offload**

1. Enable DynamoDB Streams
2. Stream to S3 via Kinesis Firehose
3. Query S3 with Athena for complex admin analytics
4. Keep DynamoDB for operational queries

### 📊 **Capacity Mode Recommendation**

- **Start:** On-Demand mode
- **After 6 months:** Evaluate switching to Provisioned if traffic is predictable
- **Use Auto-Scaling:** Target 70% utilization

### 🎯 **Key Success Factors**

1. Document access patterns rigorously
2. Monitor GSI consumption (can exceed base table)
3. Keep items < 10KB (offload media to S3)
4. Implement pagination from day one
5. Plan for analytics offload early

---

## Appendices

### A. Sample DynamoDB Table Definition (CloudFormation)

```yaml
Resources:
  ExamBuddyTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: ExamBuddyTable
      BillingMode: PAY_PER_REQUEST  # On-Demand
      AttributeDefinitions:
        - AttributeName: PK
          AttributeType: S
        - AttributeName: SK
          AttributeType: S
        - AttributeName: GSI1PK
          AttributeType: S
        - AttributeName: GSI1SK
          AttributeType: S
        - AttributeName: GSI2PK
          AttributeType: S
        - AttributeName: GSI2SK
          AttributeType: S
        - AttributeName: GSI3PK
          AttributeType: S
        - AttributeName: GSI3SK
          AttributeType: S
      KeySchema:
        - AttributeName: PK
          KeyType: HASH
        - AttributeName: SK
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: GSI1
          KeySchema:
            - AttributeName: GSI1PK
              KeyType: HASH
            - AttributeName: GSI1SK
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
        - IndexName: GSI2
          KeySchema:
            - AttributeName: GSI2PK
              KeyType: HASH
            - AttributeName: GSI2SK
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
        - IndexName: GSI3
          KeySchema:
            - AttributeName: GSI3PK
              KeyType: HASH
            - AttributeName: GSI3SK
              KeyType: RANGE
          Projection:
            ProjectionType: ALL
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: true
      Tags:
        - Key: Application
          Value: ExamBuddy
        - Key: Environment
          Value: Production
```

### B. Common Query Helper Functions

```python
# Example Python helper functions (pseudocode)

def get_user_by_email(email: str) -> dict:
    """Get user by email (login)"""
    return dynamodb.get_item(
        TableName='ExamBuddyTable',
        Key={'PK': f'USER#{email}', 'SK': f'USER#{email}'}
    )['Item']

def list_projects_by_admin(admin_id: str, archived: bool = None) -> list:
    """List projects for admin, optionally filtered by archived status"""
    if archived is not None:
        # Use GSI3 for filtered query
        return dynamodb.query(
            TableName='ExamBuddyTable',
            IndexName='GSI3',
            KeyConditionExpression='GSI3PK = :pk',
            ExpressionAttributeValues={
                ':pk': f'ADMIN#{admin_id}#STATUS#{str(archived).lower()}'
            }
        )['Items']
    else:
        # Use base table for all projects
        return dynamodb.query(
            TableName='ExamBuddyTable',
            KeyConditionExpression='PK = :pk AND begins_with(SK, :prefix)',
            ExpressionAttributeValues={
                ':pk': f'ADMIN#{admin_id}',
                ':prefix': 'PROJECT#'
            }
        )['Items']

def list_questions_by_project(project_id: str) -> list:
    """Get all questions for a project"""
    return dynamodb.query(
        TableName='ExamBuddyTable',
        KeyConditionExpression='PK = :pk AND begins_with(SK, :prefix)',
        ExpressionAttributeValues={
            ':pk': f'PROJECT#{project_id}',
            ':prefix': 'QUESTION#'
        }
    )['Items']

def list_attempts_by_candidate(candidate_id: str, limit: int = 20) -> list:
    """Get recent attempts for a candidate"""
    return dynamodb.query(
        TableName='ExamBuddyTable',
        KeyConditionExpression='PK = :pk AND begins_with(SK, :prefix)',
        ExpressionAttributeValues={
            ':pk': f'CANDIDATE#{candidate_id}',
            ':prefix': 'ATTEMPT#'
        },
        ScanIndexForward=False,  # Most recent first
        Limit=limit
    )['Items']

def list_attempts_by_project_daterange(
    project_id: str,
    start_date: str,
    end_date: str
) -> list:
    """Admin query: attempts for project in date range"""
    return dynamodb.query(
        TableName='ExamBuddyTable',
        IndexName='GSI2',
        KeyConditionExpression='GSI2PK = :pk AND GSI2SK BETWEEN :start AND :end',
        ExpressionAttributeValues={
            ':pk': f'PROJECT#{project_id}',
            ':start': f'{start_date}#',
            ':end': f'{end_date}#'
        }
    )['Items']
```

---

## References

- [AWS DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [Single-Table Design with DynamoDB](https://aws.amazon.com/blogs/compute/creating-a-single-table-design-with-amazon-dynamodb/)
- [DynamoDB Pricing](https://aws.amazon.com/dynamodb/pricing/)
- [Rick Houlihan's re:Invent Talks on Advanced Design Patterns](https://www.youtube.com/results?search_query=rick+houlihan+dynamodb)

---

**Document Version:** 1.0  
**Last Updated:** February 6, 2026  
**Author:** GitHub Copilot  
**Status:** Ready for Implementation Planning

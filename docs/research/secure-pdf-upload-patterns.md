# Secure PDF Upload Patterns for ExamBuddy Admin Question Bank

**Research Date:** February 6, 2026  
**Context:** Admin question bank management - PDF upload & parsing workflow  
**Constraints:** 10MB PDFs, 50-200 questions, Lambda 6MB request limit, Admin-only access

---

## Executive Summary

**Recommended Approach:** **Presigned POST URL** with S3 event-triggered Lambda parsing

**Rationale:**
- ✅ Handles files up to 10MB (bypasses Lambda 6MB limit)
- ✅ Direct browser → S3 upload (no Lambda proxy overhead)
- ✅ Strong security via presigned URL with IAM-enforced conditions
- ✅ Automatic parsing trigger via S3 event notifications
- ✅ Cost-effective (minimal Lambda execution time)
- ✅ Clear separation: authentication (Lambda) vs upload (S3) vs processing (Lambda)

---

## Approach Comparison Matrix

### 1. Direct Browser → Lambda (Base64-encoded)

**Flow:**
```
Admin Browser → API Gateway → Lambda (receives base64 PDF) → S3 → Parse in same Lambda
```

**Limits:**
- ❌ **BLOCKER:** Base64 encoding increases payload by ~33%
  - 10MB PDF → 13.3MB encoded → Exceeds Lambda 6MB sync request limit
  - API Gateway has 10MB limit, but Lambda itself is 6MB
- Max practical file size: ~4.5MB original (6MB encoded)

**Security:**
- ✅ Admin validation in Lambda before processing
- ✅ File type validation before S3 upload
- ✅ Integrated with API Gateway authorizer (Cognito/JWT)

**Cost:**
- 💰 Moderate: Single Lambda invocation for auth + parse
- Data transfer through Lambda (not optimal)

**Complexity:**
- 🟢 Frontend: Simple (POST with base64 body)
- 🔴 Backend: Must handle base64 decoding, larger memory allocation
- 🔴 Limited to small files

**Parse Trigger:**
- Immediate (same Lambda execution)

**Verdict:** ❌ **Not viable** for 10MB requirement due to size constraints

---

### 2. Presigned POST URL ⭐ RECOMMENDED

**Flow:**
```
1. Admin Browser → Lambda: Request upload URL (with auth check)
2. Lambda → Browser: Returns presigned POST URL + fields
3. Browser → S3: Direct upload via POST with form fields
4. S3 Event → Lambda: Triggers PDF parsing Lambda
5. Lambda: Parse PDF → Store questions in DynamoDB
```

**Limits:**
- ✅ S3 supports files up to 5GB
- ✅ No Lambda size constraint (direct S3 upload)
- ✅ API Gateway only handles small metadata request

**Security:**
- ✅ Admin validated before presigned URL generation
- ✅ Presigned URL expires (15-minute TTL)
- ✅ Enforced conditions: file size, content-type, bucket path
- ✅ S3 bucket policy restricts uploads to presigned URLs only
- ⚠️ File type validation post-upload (in parsing Lambda)

**Cost:**
- 💰💰 **Most cost-effective:**
  - Small Lambda for presigned URL generation (~100ms)
  - S3 PUT request ($0.005 per 1,000 requests)
  - Parsing Lambda only runs once upload complete
  - No data transfer through Lambda

**Complexity:**
- 🟢 Frontend: Moderate (construct multipart/form-data POST)
- 🟢 Backend: Simple presigned URL generation with boto3
- 🟢 Infrastructure: S3 event notification → Lambda trigger

**Parse Trigger:**
- S3 `s3:ObjectCreated:Post` event → Separate parsing Lambda

**Verdict:** ✅ **RECOMMENDED** - Best balance of security, cost, and scalability

---

### 3. Presigned PUT URL

**Flow:**
```
1. Admin Browser → Lambda: Request upload URL
2. Lambda → Browser: Returns presigned PUT URL
3. Browser → S3: Direct PUT with PDF binary
4. S3 Event → Lambda: Triggers parsing Lambda
```

**Limits:**
- ✅ Same as POST (up to 5GB)

**Security:**
- ✅ Similar to POST approach
- ⚠️ Slightly less granular control (no form fields for conditions)

**Cost:**
- 💰💰 Same as POST approach

**Complexity:**
- 🟢 Frontend: **Simpler** (plain PUT with binary, no multipart)
- 🟢 Backend: Slightly simpler URL generation
- 🟢 Infrastructure: Same S3 event trigger

**Parse Trigger:**
- S3 `s3:ObjectCreated:Put` event → Parsing Lambda

**Comparison with POST:**
- PUT is simpler (no multipart form encoding)
- POST allows more enforceable conditions via policy fields
- Both are valid; POST is more traditional for "form uploads"

**Verdict:** ✅ **Valid alternative** - Simpler frontend, slightly less security granularity

---

### 4. Proxy Through Lambda (Multipart Upload)

**Flow:**
```
Admin Browser → API Gateway → Lambda (streams to S3) → S3 → Parse trigger
```

**Limits:**
- ⚠️ API Gateway 10MB payload limit (meets requirement, but no headroom)
- Lambda must stream file to S3 (no in-memory buffering for 10MB)

**Security:**
- ✅ Full control: validate before S3 upload
- ✅ Admin auth + file type validation in single Lambda

**Cost:**
- 💰💰💰 **Most expensive:**
  - Large Lambda invocation duration (streaming 10MB)
  - Lambda data transfer charges
  - Higher memory allocation required

**Complexity:**
- 🔴 Frontend: Must send multipart/form-data
- 🔴 Backend: Complex streaming logic to avoid memory limits
- 🟡 Infrastructure: No S3 event needed (can parse in same Lambda)

**Parse Trigger:**
- Can parse immediately after upload in same Lambda, OR
- S3 event → Separate Lambda

**Verdict:** ⚠️ **Not recommended** - More complex and costly than presigned URL

---

## Recommended Architecture: Presigned POST URL

### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 1: Authentication & Presigned URL Generation                  │
└─────────────────────────────────────────────────────────────────────┘

[Admin Browser]
      │ 1. POST /api/admin/upload/presigned
      │    Headers: { Authorization: Bearer <jwt> }
      │    Body: { filename: "exam.pdf", contentType: "application/pdf" }
      ↓
[API Gateway]
      │ 2. Cognito Authorizer validates JWT
      │    Checks: user is admin group
      ↓
[Lambda: generate-presigned-url]
      │ 3. Validates request (filename, content type)
      │ 4. Generates unique S3 key: admin-uploads/{userId}/{timestamp}-{filename}
      │ 5. Creates presigned POST URL with conditions:
      │    - Max size: 10MB
      │    - Content-Type: application/pdf
      │    - Expiry: 15 minutes
      │ 6. Stores metadata in DynamoDB: { uploadId, userId, status: "pending", createdAt }
      ↓
[Admin Browser]
      │ 7. Receives: { uploadUrl, fields: {...}, uploadId }


┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 2: Direct S3 Upload                                           │
└─────────────────────────────────────────────────────────────────────┘

[Admin Browser]
      │ 8. Constructs multipart/form-data POST:
      │    - Include all fields from presigned response
      │    - Append PDF file
      │ 9. POST to S3 presigned URL (direct, bypasses Lambda)
      ↓
[S3 Bucket: exambuddy-admin-uploads]
      │ 10. Validates presigned URL signature
      │ 11. Validates conditions (size, content-type)
      │ 12. Stores file: admin-uploads/{userId}/{timestamp}-exam.pdf
      │ 13. Returns 204 No Content (success)
      ↓
[Admin Browser]
      │ 14. Poll status: GET /api/admin/upload/{uploadId}/status


┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 3: Automated PDF Parsing                                      │
└─────────────────────────────────────────────────────────────────────┘

[S3 Event Notification]
      │ 15. Triggers on s3:ObjectCreated:Post
      │     Filter: prefix="admin-uploads/", suffix=".pdf"
      ↓
[Lambda: parse-pdf-questions]
      │ 16. Retrieves PDF from S3
      │ 17. Extracts metadata from S3 key (userId, uploadId)
      │ 18. Validates file:
      │     - Content-Type verification
      │     - PDF structure validation
      │     - Virus scan (optional: integrate ClamAV)
      │ 19. Parses PDF (library: pdfplumber or PyPDF2)
      │ 20. Extracts 50-200 questions
      │ 21. Batch writes to DynamoDB:
      │     - Table: Questions
      │     - Items: { questionId, examId, text, options, answer, uploadId }
      │ 22. Updates upload status in DynamoDB:
      │     - { uploadId, status: "completed", questionCount, processedAt }
      │ 23. Sends notification (SNS/SES) to admin
      ↓
[DynamoDB: Questions Table]
      │ Questions stored and indexed


┌─────────────────────────────────────────────────────────────────────┐
│ PHASE 4: Status Polling & Completion                                │
└─────────────────────────────────────────────────────────────────────┘

[Admin Browser]
      │ 24. Polls: GET /api/admin/upload/{uploadId}/status
      │     Response: { status: "completed", questionCount: 150 }
      │ 25. Redirects to question bank management UI
      ↓
[Frontend: Question Bank Page]
      │ Display newly imported questions
```

---

## Implementation Code Samples

### Backend: Generate Presigned POST URL (Python + FastAPI)

```python
# lambda_functions/generate_presigned_url/handler.py

import boto3
import json
import os
from datetime import datetime, timedelta
from mangum import Mangum
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uuid

app = FastAPI()
s3_client = boto3.client('s3', region_name=os.environ['AWS_REGION'])
dynamodb = boto3.resource('dynamodb')
uploads_table = dynamodb.Table(os.environ['UPLOADS_TABLE'])

BUCKET_NAME = os.environ['UPLOAD_BUCKET']
EXPIRATION = 900  # 15 minutes
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class PresignedURLRequest(BaseModel):
    filename: str
    contentType: str = "application/pdf"


def get_current_user(authorization: str):
    """Extract user from JWT - integrate with Cognito authorizer"""
    # In production, this would be populated by API Gateway Cognito authorizer
    # Access via event['requestContext']['authorizer']['claims']
    # For now, mock structure:
    return {
        "userId": "admin-user-123",
        "email": "admin@exambuddy.com",
        "groups": ["Admins"]
    }


@app.post("/api/admin/upload/presigned")
async def generate_presigned_url(
    request: PresignedURLRequest,
    authorization: str = None  # In real impl: Header(...)
):
    """Generate presigned POST URL for admin PDF upload"""
    
    # 1. Validate user is admin (in prod, use Cognito authorizer)
    user = get_current_user(authorization)
    if "Admins" not in user.get("groups", []):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # 2. Validate file type
    if request.contentType != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    # 3. Sanitize filename
    safe_filename = "".join(c for c in request.filename if c.isalnum() or c in ".-_")
    if not safe_filename.endswith(".pdf"):
        safe_filename += ".pdf"
    
    # 4. Generate unique S3 key
    upload_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    s3_key = f"admin-uploads/{user['userId']}/{timestamp}-{safe_filename}"
    
    # 5. Create presigned POST URL with conditions
    try:
        presigned_post = s3_client.generate_presigned_post(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Fields={
                "Content-Type": request.contentType,
                "x-amz-meta-upload-id": upload_id,
                "x-amz-meta-user-id": user['userId'],
            },
            Conditions=[
                {"Content-Type": request.contentType},
                ["content-length-range", 1, MAX_FILE_SIZE],
                {"x-amz-meta-upload-id": upload_id},
                {"x-amz-meta-user-id": user['userId']},
            ],
            ExpiresIn=EXPIRATION
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate presigned URL: {str(e)}")
    
    # 6. Store upload metadata in DynamoDB
    uploads_table.put_item(Item={
        "uploadId": upload_id,
        "userId": user['userId'],
        "filename": safe_filename,
        "s3Key": s3_key,
        "status": "pending",
        "createdAt": datetime.utcnow().isoformat(),
        "expiresAt": (datetime.utcnow() + timedelta(seconds=EXPIRATION)).isoformat()
    })
    
    # 7. Return presigned URL and fields
    return {
        "uploadId": upload_id,
        "uploadUrl": presigned_post['url'],
        "fields": presigned_post['fields'],
        "expiresIn": EXPIRATION
    }


@app.get("/api/admin/upload/{upload_id}/status")
async def get_upload_status(upload_id: str):
    """Check upload and parsing status"""
    
    try:
        response = uploads_table.get_item(Key={"uploadId": upload_id})
        
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        item = response["Item"]
        return {
            "uploadId": upload_id,
            "status": item["status"],  # pending, completed, failed
            "filename": item["filename"],
            "questionCount": item.get("questionCount"),
            "error": item.get("error"),
            "createdAt": item["createdAt"],
            "processedAt": item.get("processedAt")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Mangum handler for Lambda
handler = Mangum(app)
```

---

### Frontend: Upload with Presigned POST (React + TypeScript)

```typescript
// frontend/src/services/uploadService.ts

interface PresignedPostResponse {
  uploadId: string;
  uploadUrl: string;
  fields: Record<string, string>;
  expiresIn: number;
}

interface UploadStatus {
  uploadId: string;
  status: 'pending' | 'completed' | 'failed';
  filename: string;
  questionCount?: number;
  error?: string;
}

class AdminUploadService {
  private apiBaseUrl = process.env.REACT_APP_API_URL;

  /**
   * Step 1: Request presigned POST URL from backend
   */
  async requestPresignedUrl(
    file: File,
    authToken: string
  ): Promise<PresignedPostResponse> {
    const response = await fetch(`${this.apiBaseUrl}/api/admin/upload/presigned`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`,
      },
      body: JSON.stringify({
        filename: file.name,
        contentType: file.type,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get upload URL');
    }

    return response.json();
  }

  /**
   * Step 2: Upload PDF directly to S3 using presigned POST
   */
  async uploadToS3(
    file: File,
    presignedPost: PresignedPostResponse,
    onProgress?: (percent: number) => void
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      const formData = new FormData();

      // IMPORTANT: Add presigned fields BEFORE the file
      Object.entries(presignedPost.fields).forEach(([key, value]) => {
        formData.append(key, value);
      });

      // File must be LAST
      formData.append('file', file);

      const xhr = new XMLHttpRequest();

      // Track upload progress
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable && onProgress) {
          const percent = Math.round((e.loaded / e.total) * 100);
          onProgress(percent);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status === 204 || xhr.status === 200) {
          resolve();
        } else {
          reject(new Error(`Upload failed with status ${xhr.status}`));
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('Network error during upload'));
      });

      xhr.addEventListener('abort', () => {
        reject(new Error('Upload cancelled'));
      });

      xhr.open('POST', presignedPost.uploadUrl);
      xhr.send(formData);
    });
  }

  /**
   * Step 3: Poll upload status until processing completes
   */
  async pollUploadStatus(
    uploadId: string,
    authToken: string,
    maxAttempts: number = 30,
    intervalMs: number = 2000
  ): Promise<UploadStatus> {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      const response = await fetch(
        `${this.apiBaseUrl}/api/admin/upload/${uploadId}/status`,
        {
          headers: {
            'Authorization': `Bearer ${authToken}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to check upload status');
      }

      const status: UploadStatus = await response.json();

      if (status.status === 'completed') {
        return status;
      }

      if (status.status === 'failed') {
        throw new Error(status.error || 'Upload processing failed');
      }

      // Still pending, wait before next poll
      await new Promise(resolve => setTimeout(resolve, intervalMs));
    }

    throw new Error('Upload processing timeout');
  }

  /**
   * Complete upload flow: request URL → upload → poll status
   */
  async uploadPDF(
    file: File,
    authToken: string,
    onProgress?: (percent: number) => void
  ): Promise<UploadStatus> {
    // Validate file before upload
    if (file.type !== 'application/pdf') {
      throw new Error('Only PDF files are allowed');
    }

    if (file.size > 10 * 1024 * 1024) {
      throw new Error('File size must be less than 10MB');
    }

    // Step 1: Get presigned URL
    onProgress?.(5);
    const presignedPost = await this.requestPresignedUrl(file, authToken);

    // Step 2: Upload to S3
    await this.uploadToS3(file, presignedPost, (percent) => {
      // Map 0-100% upload to 5-70% overall progress
      onProgress?.(5 + (percent * 0.65));
    });

    // Step 3: Poll for processing completion
    onProgress?.(70);
    const result = await this.pollUploadStatus(presignedPost.uploadId, authToken);
    onProgress?.(100);

    return result;
  }
}

export const uploadService = new AdminUploadService();
```

---

### Frontend: React Upload Component

```tsx
// frontend/src/components/QuestionBankUpload.tsx

import React, { useState } from 'react';
import { uploadService } from '../services/uploadService';
import { useAuth } from '../contexts/AuthContext';

export const QuestionBankUpload: React.FC = () => {
  const { authToken } = useAuth();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Client-side validation
    if (file.type !== 'application/pdf') {
      setError('Only PDF files are allowed');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    setSelectedFile(file);
    setError(null);
  };

  const handleUpload = async () => {
    if (!selectedFile || !authToken) return;

    setUploading(true);
    setProgress(0);
    setError(null);
    setResult(null);

    try {
      const uploadResult = await uploadService.uploadPDF(
        selectedFile,
        authToken,
        setProgress
      );

      setResult(uploadResult);
      setSelectedFile(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload Question Bank PDF</h2>

      <div className="file-input">
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileSelect}
          disabled={uploading}
        />
        {selectedFile && (
          <p>Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)</p>
        )}
      </div>

      {error && <div className="error">{error}</div>}

      {uploading && (
        <div className="progress">
          <div className="progress-bar" style={{ width: `${progress}%` }}>
            {progress}%
          </div>
          <p>
            {progress < 70 ? 'Uploading...' : 'Processing PDF...'}
          </p>
        </div>
      )}

      {result && (
        <div className="success">
          ✅ Upload complete! {result.questionCount} questions imported.
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!selectedFile || uploading}
      >
        {uploading ? 'Uploading...' : 'Upload PDF'}
      </button>
    </div>
  );
};
```

---

### Backend: PDF Parsing Lambda (S3 Event Trigger)

```python
# lambda_functions/parse_pdf_questions/handler.py

import boto3
import json
import os
from datetime import datetime
import pdfplumber
from io import BytesIO
import re

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
uploads_table = dynamodb.Table(os.environ['UPLOADS_TABLE'])
questions_table = dynamodb.Table(os.environ['QUESTIONS_TABLE'])


def lambda_handler(event, context):
    """
    Triggered by S3 event when PDF is uploaded
    Parses PDF and stores questions in DynamoDB
    """
    
    # Extract S3 event details
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        print(f"Processing PDF: s3://{bucket}/{key}")
        
        try:
            # Extract metadata from S3 key
            # Format: admin-uploads/{userId}/{timestamp}-{filename}
            parts = key.split('/')
            user_id = parts[1] if len(parts) > 1 else 'unknown'
            
            # Get object metadata
            s3_object = s3_client.get_object(Bucket=bucket, Key=key)
            upload_id = s3_object['Metadata'].get('upload-id', 'unknown')
            
            # Download PDF
            pdf_bytes = s3_object['Body'].read()
            
            # Validate file is actually a PDF
            if not pdf_bytes.startswith(b'%PDF'):
                raise ValueError("File is not a valid PDF")
            
            # Parse PDF
            questions = parse_pdf_questions(pdf_bytes)
            
            if len(questions) < 10:
                raise ValueError(f"Too few questions extracted: {len(questions)}")
            
            # Store questions in DynamoDB
            store_questions(questions, upload_id, user_id)
            
            # Update upload status
            uploads_table.update_item(
                Key={"uploadId": upload_id},
                UpdateExpression="SET #status = :status, questionCount = :count, processedAt = :timestamp",
                ExpressionAttributeNames={
                    "#status": "status"
                },
                ExpressionAttributeValues={
                    ":status": "completed",
                    ":count": len(questions),
                    ":timestamp": datetime.utcnow().isoformat()
                }
            )
            
            print(f"Successfully processed {len(questions)} questions")
            
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            
            # Update upload status to failed
            try:
                uploads_table.update_item(
                    Key={"uploadId": upload_id},
                    UpdateExpression="SET #status = :status, error = :error, processedAt = :timestamp",
                    ExpressionAttributeNames={
                        "#status": "status"
                    },
                    ExpressionAttributeValues={
                        ":status": "failed",
                        ":error": str(e),
                        ":timestamp": datetime.utcnow().isoformat()
                    }
                )
            except Exception as update_error:
                print(f"Failed to update error status: {str(update_error)}")
            
            raise
    
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "PDF processing complete"})
    }


def parse_pdf_questions(pdf_bytes: bytes) -> list:
    """
    Extract questions from PDF using pdfplumber
    Expected format: Multiple choice questions with A, B, C, D options
    """
    questions = []
    
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
        
        # Pattern for question blocks
        # Example format:
        # 1. What is the capital of France?
        # A) London
        # B) Paris
        # C) Berlin
        # D) Madrid
        # Answer: B
        
        question_pattern = r'(\d+)\.\s+(.+?)\n\s*A\)\s*(.+?)\n\s*B\)\s*(.+?)\n\s*C\)\s*(.+?)\n\s*D\)\s*(.+?)\n\s*(?:Answer|Correct):\s*([A-D])'
        
        matches = re.finditer(question_pattern, full_text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            question_num, question_text, opt_a, opt_b, opt_c, opt_d, answer = match.groups()
            
            questions.append({
                "questionNumber": int(question_num.strip()),
                "questionText": question_text.strip(),
                "options": {
                    "A": opt_a.strip(),
                    "B": opt_b.strip(),
                    "C": opt_c.strip(),
                    "D": opt_d.strip()
                },
                "correctAnswer": answer.strip().upper()
            })
    
    return questions


def store_questions(questions: list, upload_id: str, user_id: str):
    """
    Batch write questions to DynamoDB
    """
    with questions_table.batch_writer() as batch:
        for question in questions:
            batch.put_item(Item={
                "questionId": f"{upload_id}#{question['questionNumber']}",
                "uploadId": upload_id,
                "userId": user_id,
                "questionNumber": question['questionNumber'],
                "questionText": question['questionText'],
                "options": question['options'],
                "correctAnswer": question['correctAnswer'],
                "createdAt": datetime.utcnow().isoformat(),
                "status": "active"
            })
```

---

## S3 Bucket Configuration

### Bucket Policy (Restrict to Presigned URLs Only)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowPresignedUploadsOnly",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::exambuddy-admin-uploads/admin-uploads/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    },
    {
      "Sid": "AllowLambdaRead",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT_ID:role/parse-pdf-lambda-role"
      },
      "Action": [
        "s3:GetObject",
        "s3:GetObjectMetadata"
      ],
      "Resource": "arn:aws:s3:::exambuddy-admin-uploads/*"
    }
  ]
}
```

### CORS Configuration

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["POST", "PUT"],
    "AllowedOrigins": [
      "https://exambuddy.com",
      "https://admin.exambuddy.com",
      "http://localhost:3000"
    ],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

### S3 Event Notification (Lambda Trigger)

```json
{
  "LambdaFunctionConfigurations": [
    {
      "Id": "ParsePDFOnUpload",
      "LambdaFunctionArn": "arn:aws:lambda:us-east-1:ACCOUNT_ID:function:parse-pdf-questions",
      "Events": ["s3:ObjectCreated:Post", "s3:ObjectCreated:Put"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "prefix",
              "Value": "admin-uploads/"
            },
            {
              "Name": "suffix",
              "Value": ".pdf"
            }
          ]
        }
      }
    }
  ]
}
```

### Lifecycle Policy (Auto-delete After 30 Days)

```json
{
  "Rules": [
    {
      "Id": "DeleteOldUploads",
      "Status": "Enabled",
      "Prefix": "admin-uploads/",
      "Expiration": {
        "Days": 30
      },
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 1
      }
    }
  ]
}
```

---

## Security Considerations

### 1. Authentication & Authorization

**Lambda Authorizer (Cognito)**
```python
# API Gateway Cognito Authorizer configuration
{
  "Type": "COGNITO_USER_POOLS",
  "IdentitySource": "$request.header.Authorization",
  "UserPoolArn": "arn:aws:cognito-idp:region:account:userpool/pool-id",
  "Claims": ["cognito:groups"]
}
```

**Admin Group Check**
```python
def validate_admin(event):
    claims = event['requestContext']['authorizer']['claims']
    groups = json.loads(claims.get('cognito:groups', '[]'))
    if 'Admins' not in groups:
        raise Exception('Unauthorized: Admin access required')
```

### 2. File Validation Strategy

**Pre-Upload (Client-Side)**
- ✅ File extension check (.pdf only)
- ✅ File size validation (< 10MB)
- ✅ MIME type check (application/pdf)
- ⚠️ Can be bypassed by malicious users

**Pre-Upload (Server-Side - Presigned URL Generation)**
- ✅ Admin authentication
- ✅ Enforce content-type in presigned policy
- ✅ Enforce max file size in presigned conditions
- ✅ Unique S3 key prevents overwriting

**Post-Upload (Parsing Lambda)**
- ✅ **Magic bytes validation** (file starts with `%PDF`)
- ✅ PDF structure validation via parsing library
- ✅ Optional: Virus scanning with ClamAV Lambda layer
- ✅ Content validation (minimum question count)

**Recommended Layers of Validation:**
```python
# Layer 1: Client-side (UX feedback)
if file.type != 'application/pdf' or file.size > 10MB:
    show_error()

# Layer 2: Presigned URL conditions (enforced by S3)
conditions = [
    {"Content-Type": "application/pdf"},
    ["content-length-range", 1, 10485760]
]

# Layer 3: Parsing Lambda (security)
if not pdf_bytes.startswith(b'%PDF'):
    raise ValueError("Invalid PDF")

# Layer 4: Content validation
if len(questions) < 10 or len(questions) > 300:
    raise ValueError("Question count out of range")
```

### 3. Rate Limiting

**API Gateway Throttling**
```yaml
# serverless.yml or CloudFormation
resources:
  Resources:
    ApiGatewayRestApi:
      Properties:
        ThrottleSettings:
          RateLimit: 10  # requests per second
          BurstLimit: 20
```

**Per-User Upload Limits**
```python
# Check upload count in DynamoDB before generating presigned URL
def check_upload_limit(user_id: str) -> bool:
    # Allow max 5 uploads per day per user
    today = datetime.utcnow().date().isoformat()
    
    response = uploads_table.query(
        IndexName="UserIdDateIndex",
        KeyConditionExpression="userId = :uid AND begins_with(createdAt, :date)",
        ExpressionAttributeValues={
            ":uid": user_id,
            ":date": today
        }
    )
    
    return response['Count'] < 5
```

### 4. S3 Bucket Hardening

```yaml
# Terraform / CloudFormation configuration
BucketEncryption:
  ServerSideEncryptionConfiguration:
    - ServerSideEncryptionByDefault:
        SSEAlgorithm: AES256

PublicAccessBlockConfiguration:
  BlockPublicAcls: true
  BlockPublicPolicy: true
  IgnorePublicAcls: true
  RestrictPublicBuckets: true

VersioningConfiguration:
  Status: Enabled  # Allow recovery from accidental deletion

LoggingConfiguration:
  DestinationBucketName: exambuddy-logs
  LogFilePrefix: s3-access/

ObjectLockConfiguration:
  ObjectLockEnabled: Disabled  # Enable if compliance required
```

---

## Error Handling Strategies

### 1. Upload Errors (Frontend)

```typescript
class UploadError extends Error {
  constructor(
    message: string,
    public code: string,
    public retryable: boolean = false
  ) {
    super(message);
  }
}

async function handleUploadError(error: Error): Promise<void> {
  if (error.message.includes('Network error')) {
    // Network failure - retryable
    throw new UploadError(
      'Network error. Please check your connection and try again.',
      'NETWORK_ERROR',
      true
    );
  }
  
  if (error.message.includes('status 403')) {
    // Presigned URL expired or invalid
    throw new UploadError(
      'Upload session expired. Please try again.',
      'EXPIRED_URL',
      true
    );
  }
  
  if (error.message.includes('EntityTooLarge')) {
    // File size exceeded
    throw new UploadError(
      'File size exceeds 10MB limit.',
      'FILE_TOO_LARGE',
      false
    );
  }
  
  // Unknown error
  throw new UploadError(
    'Upload failed. Please contact support.',
    'UNKNOWN_ERROR',
    false
  );
}
```

### 2. Parsing Errors (Backend)

```python
class PDFParsingError(Exception):
    """Base exception for PDF parsing errors"""
    pass

class InvalidPDFStructure(PDFParsingError):
    """Raised when PDF structure is invalid"""
    pass

class InsufficientQuestions(PDFParsingError):
    """Raised when question count is too low"""
    pass

def handle_parsing_failure(upload_id: str, error: Exception):
    """Store detailed error information for admin review"""
    
    error_details = {
        "errorType": type(error).__name__,
        "errorMessage": str(error),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Map to user-friendly messages
    user_message = {
        "InvalidPDFStructure": "The PDF file is corrupted or in an unsupported format.",
        "InsufficientQuestions": "The PDF contains too few questions. Expected 50-200 questions.",
        "PDFParsingError": "Unable to extract questions from PDF. Please check the file format."
    }.get(error_details["errorType"], "An error occurred while processing the PDF.")
    
    # Update DynamoDB with error details
    uploads_table.update_item(
        Key={"uploadId": upload_id},
        UpdateExpression="SET #status = :status, error = :error, errorDetails = :details, processedAt = :timestamp",
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={
            ":status": "failed",
            ":error": user_message,
            ":details": error_details,
            ":timestamp": datetime.utcnow().isoformat()
        }
    )
    
    # Optionally: Send email to admin with error details
    # sns_client.publish(TopicArn=..., Message=...)
```

### 3. Retry Logic (Frontend)

```typescript
async function uploadWithRetry(
  file: File,
  authToken: string,
  maxRetries: number = 3
): Promise<UploadStatus> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await uploadService.uploadPDF(file, authToken);
    } catch (error) {
      const uploadError = error as UploadError;
      
      if (!uploadError.retryable || attempt === maxRetries) {
        throw error;
      }
      
      // Exponential backoff
      const delay = Math.pow(2, attempt) * 1000;
      console.log(`Upload failed, retrying in ${delay}ms (attempt ${attempt}/${maxRetries})`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw new Error('Upload failed after maximum retries');
}
```

---

## Cost Analysis

### Presigned POST Approach (Recommended)

**Per PDF Upload (10MB, 150 questions)**

| Service | Usage | Cost per Upload | Monthly Cost (100 uploads) |
|---------|-------|-----------------|----------------------------|
| **Lambda (Presigned URL)** | 100ms @ 128MB | $0.0000002 | $0.00002 |
| **Lambda (PDF Parsing)** | 5s @ 512MB | $0.0000042 | $0.00042 |
| **S3 PUT Request** | 1 request | $0.000005 | $0.0005 |
| **S3 Storage** | 10MB × 30 days | $0.0023 | $0.23 |
| **DynamoDB Writes** | 151 items (1 upload + 150 questions) | $0.0019 | $0.19 |
| **Data Transfer** | 0 (direct S3 upload) | $0 | $0 |
| **TOTAL** | | **$0.0042** | **$0.42** |

**Comparison: Proxy Through Lambda**

| Service | Usage | Cost per Upload | Monthly Cost (100 uploads) |
|---------|-------|-----------------|----------------------------|
| **Lambda (Proxy + Parse)** | 15s @ 1024MB | $0.000025 | $0.0025 |
| **S3 PUT Request** | 1 request | $0.000005 | $0.0005 |
| **S3 Storage** | 10MB × 30 days | $0.0023 | $0.23 |
| **DynamoDB Writes** | 151 items | $0.0019 | $0.19 |
| **Data Transfer (Lambda → S3)** | 10MB | $0.0009 | $0.09 |
| **TOTAL** | | **$0.0072** | **$0.72** |

**Savings: 42% cheaper with presigned POST approach**

---

## Infrastructure as Code (Terraform)

```hcl
# terraform/s3.tf

resource "aws_s3_bucket" "admin_uploads" {
  bucket = "exambuddy-admin-uploads"
}

resource "aws_s3_bucket_cors_configuration" "admin_uploads" {
  bucket = aws_s3_bucket.admin_uploads.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["POST", "PUT"]
    allowed_origins = ["https://exambuddy.com", "http://localhost:3000"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket_notification" "pdf_upload" {
  bucket = aws_s3_bucket.admin_uploads.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.parse_pdf.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "admin-uploads/"
    filter_suffix       = ".pdf"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.parse_pdf.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.admin_uploads.arn
}

resource "aws_s3_bucket_lifecycle_configuration" "admin_uploads" {
  bucket = aws_s3_bucket.admin_uploads.id

  rule {
    id     = "delete-old-uploads"
    status = "Enabled"

    filter {
      prefix = "admin-uploads/"
    }

    expiration {
      days = 30
    }
  }
}
```

---

## Testing Checklist

### Unit Tests

- [ ] Presigned URL generation with correct conditions
- [ ] File size validation
- [ ] Content-Type validation
- [ ] PDF parsing logic with sample PDFs
- [ ] Question extraction regex patterns
- [ ] DynamoDB batch write operations

### Integration Tests

- [ ] End-to-end upload flow (presigned URL → S3 → Lambda trigger)
- [ ] Expired presigned URL rejection
- [ ] File size limit enforcement (try 11MB file)
- [ ] Wrong content-type rejection
- [ ] S3 event notification delivery to Lambda
- [ ] DynamoDB status updates

### Security Tests

- [ ] Non-admin user cannot generate presigned URL
- [ ] Presigned URL expires after 15 minutes
- [ ] Cannot upload to different S3 key than presigned
- [ ] CORS blocks unauthorized origins
- [ ] Invalid JWT rejected by authorizer

### Performance Tests

- [ ] Concurrent uploads (10 admins uploading simultaneously)
- [ ] Large PDF (10MB, 200 questions)
- [ ] Lambda cold start time
- [ ] Parsing Lambda timeout (< 30s for 10MB PDF)

---

## Monitoring & Observability

### CloudWatch Metrics

```python
# Custom metrics in Lambda functions
import boto3

cloudwatch = boto3.client('cloudwatch')

def track_upload_metrics(upload_id: str, file_size: int, question_count: int, duration: float):
    cloudwatch.put_metric_data(
        Namespace='ExamBuddy/Uploads',
        MetricData=[
            {
                'MetricName': 'PDFFileSize',
                'Value': file_size,
                'Unit': 'Bytes'
            },
            {
                'MetricName': 'QuestionCount',
                'Value': question_count,
                'Unit': 'Count'
            },
            {
                'MetricName': 'ParsingDuration',
                'Value': duration,
                'Unit': 'Seconds'
            }
        ]
    )
```

### CloudWatch Alarms

```yaml
# CloudFormation / Terraform
ParsingFailureAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: ExamBuddy-PDF-Parsing-Failures
    MetricName: Errors
    Namespace: AWS/Lambda
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 1
    Threshold: 3
    ComparisonOperator: GreaterThanThreshold
    Dimensions:
      - Name: FunctionName
        Value: parse-pdf-questions
    AlarmActions:
      - !Ref AdminSNSTopic
```

### Logging Strategy

```python
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log_structured(event_type: str, **kwargs):
    """Structured logging for CloudWatch Insights queries"""
    log_entry = {
        "eventType": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        **kwargs
    }
    logger.info(json.dumps(log_entry))

# Usage:
log_structured("upload_started", uploadId=upload_id, userId=user_id, fileSize=file_size)
log_structured("parsing_complete", uploadId=upload_id, questionCount=len(questions))
```

### CloudWatch Insights Queries

```sql
-- Failed uploads in last 24 hours
fields @timestamp, uploadId, error
| filter eventType = "parsing_failed"
| sort @timestamp desc
| limit 20

-- Average parsing duration by file size
fields fileSize, parsingDuration
| filter eventType = "parsing_complete"
| stats avg(parsingDuration) by bin(fileSize, 1000000)

-- Upload success rate
fields @timestamp
| filter eventType in ["upload_started", "parsing_complete", "parsing_failed"]
| stats count() by eventType
```

---

## Alternative: Presigned PUT URL (Simpler Frontend)

If you prefer simpler frontend code, use **Presigned PUT** instead of POST:

### Backend Changes

```python
# Use generate_presigned_url instead of generate_presigned_post
presigned_url = s3_client.generate_presigned_url(
    ClientMethod='put_object',
    Params={
        'Bucket': BUCKET_NAME,
        'Key': s3_key,
        'ContentType': 'application/pdf',
        'Metadata': {
            'upload-id': upload_id,
            'user-id': user['userId']
        }
    },
    ExpiresIn=EXPIRATION
)

return {
    "uploadId": upload_id,
    "uploadUrl": presigned_url,
    "method": "PUT",
    "expiresIn": EXPIRATION
}
```

### Frontend Changes

```typescript
// Much simpler: plain PUT with binary body
async uploadToS3(file: File, presignedUrl: string): Promise<void> {
  const response = await fetch(presignedUrl, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/pdf',
    },
    body: file, // Direct binary upload, no FormData
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }
}
```

**Tradeoffs:**
- ✅ Simpler frontend (no multipart/form-data)
- ⚠️ Slightly less security control (no presigned POST policy fields)
- ✅ Still enforces content-type and expiration
- ✅ Same performance and cost

---

## Conclusion

The **Presigned POST URL** approach provides the optimal balance for ExamBuddy:

1. **Handles 10MB PDFs** without hitting Lambda limits
2. **Secure** via IAM-enforced presigned URL conditions
3. **Cost-effective** at $0.004 per upload
4. **Scalable** with direct browser → S3 upload
5. **Automated** with S3 event-triggered parsing
6. **Admin-controlled** via Cognito authorizer

### Next Steps for Implementation

1. **Week 1:** Set up S3 bucket with CORS and event notifications
2. **Week 2:** Implement presigned URL generation Lambda + API Gateway
3. **Week 3:** Build parsing Lambda with pdfplumber
4. **Week 4:** Frontend upload component with progress tracking
5. **Week 5:** Testing, monitoring, and security audit

### Resources

- [AWS S3 Presigned URLs Documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html)
- [pdfplumber Library](https://github.com/jsvine/pdfplumber)
- [API Gateway File Upload Limits](https://docs.aws.amazon.com/apigateway/latest/developerguide/limits.html)
- [Lambda Quotas](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html)

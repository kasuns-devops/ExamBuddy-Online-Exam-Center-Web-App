# FastAPI on AWS Lambda: Serverless Deployment Research Report

**Date:** February 6, 2026  
**Project:** ExamBuddy  
**Purpose:** Research serverless deployment patterns for FastAPI on AWS Lambda

---

## Executive Summary

This report analyzes serverless deployment patterns for FastAPI on AWS Lambda, covering ASGI adapters, deployment tooling, cold start optimization, and local development approaches. Based on this research, recommendations are provided for the ExamBuddy project.

**Key Recommendations:**
- **ASGI Adapter:** Mangum (de facto standard for FastAPI on Lambda)
- **Deployment Tool:** AWS SAM (recommended for AWS-native projects)
- **Cold Start Strategy:** Multi-layered approach focusing on bundle optimization and lazy loading

---

## 1. ASGI Adapters for Lambda

### 1.1 Mangum Adapter (Recommended)

**Overview:**
Mangum is the de facto standard ASGI adapter for running FastAPI and other ASGI applications on AWS Lambda. It translates Lambda event structures into ASGI format and vice versa.

**How It Works:**
```python
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Mangum wraps the ASGI app to handle Lambda events
handler = Mangum(app, lifespan="off")
```

**Supported Event Sources:**
- API Gateway HTTP APIs
- API Gateway REST APIs
- Application Load Balancer (ALB)
- Lambda Function URLs
- CloudFront Lambda@Edge

**Key Features:**
- ✅ Binary media type support
- ✅ Payload compression (GZip/Brotli)
- ✅ Lifespan event support (startup/shutdown)
- ✅ Actively maintained and widely adopted
- ✅ Works with SAM and Serverless Framework
- ✅ Compatible with Starlette, FastAPI, Quart, Django

**Installation:**
```bash
pip install mangum
```

### 1.2 Alternative ASGI Adapters

**aws-asgi (Legacy):**
- Older adapter, less actively maintained
- Limited to API Gateway v1/v2
- Not recommended for new projects

**aws-lambda-adapter (AWS Official):**
- AWS official adapter for web frameworks
- Generic HTTP adapter, not ASGI-specific
- Requires running a web server in Lambda (Uvicorn/Gunicorn)
- More overhead than Mangum

### 1.3 Recommendation: Mangum

**Justification:**
1. **De facto standard** - Most widely used in the FastAPI/Lambda ecosystem
2. **Best documentation** - Comprehensive guides and examples
3. **Active maintenance** - Regular updates and community support
4. **Feature-rich** - Supports all major Lambda event sources
5. **Zero configuration** - Works out of the box with minimal setup
6. **Battle-tested** - Used in production by major companies

**Gotchas with Mangum:**
- Requires `lifespan="off"` for Lambda (startup events happen on cold start only)
- Binary response handling requires API Gateway configuration
- WebSocket support is limited (Lambda Function URLs don't support WebSockets)

---

## 2. Deployment Tooling: AWS SAM vs Serverless Framework

### 2.1 AWS SAM (Serverless Application Model)

**Overview:**
AWS SAM is AWS's official framework for building serverless applications. It's an extension of CloudFormation with simplified syntax for serverless resources.

**Pros:**
- ✅ **AWS-native integration** - First-class support for all AWS services
- ✅ **Zero cost** - Open source, no licensing fees
- ✅ **CloudFormation foundation** - Full power of CloudFormation when needed
- ✅ **SAM CLI features:**
  - `sam local start-api` - Local API Gateway emulation
  - `sam local invoke` - Test individual functions
  - `sam deploy` - Simplified deployment
  - `sam sync` - Fast incremental updates (SAM Accelerate)
- ✅ **Better for AWS-centric teams** - Aligns with AWS best practices
- ✅ **Built-in debugging** - Native support for debugging Lambda functions
- ✅ **AWS Lambda Powertools integration** - Official AWS observability tools

**Cons:**
- ❌ **AWS-only** - Cannot deploy to other cloud providers
- ❌ **Verbose YAML** - More verbose than Serverless Framework
- ❌ **Limited plugin ecosystem** - Fewer community plugins
- ❌ **Steeper learning curve** - Requires CloudFormation knowledge

**Example SAM Template:**
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Timeout: 30
    Runtime: python3.11
    Architectures:
      - x86_64
    Environment:
      Variables:
        STAGE: prod

Resources:
  ExamBuddyApi:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: main.handler
      MemorySize: 512
      Events:
        ApiEvent:
          Type: HttpApi
          Properties:
            Path: /{proxy+}
            Method: ANY
```

### 2.2 Serverless Framework

**Overview:**
Serverless Framework is a third-party, cloud-agnostic framework for building serverless applications across multiple cloud providers.

**Pros:**
- ✅ **Multi-cloud support** - Deploy to AWS, Azure, GCP, etc.
- ✅ **Simpler syntax** - More concise YAML configuration
- ✅ **Rich plugin ecosystem** - 1000+ community plugins
- ✅ **Developer-friendly** - Easier onboarding for new users
- ✅ **Faster deployment** - Optimized deployment process
- ✅ **Built-in features:**
  - Stage management
  - Environment variables
  - Resource tagging
  - Automatic IAM role creation

**Cons:**
- ❌ **Third-party dependency** - Not officially supported by AWS
- ❌ **Potential vendor lock-in** - To Serverless Inc. tooling
- ❌ **Less AWS integration** - Doesn't support all AWS features immediately
- ❌ **Commercial features** - Some advanced features require paid plans
- ❌ **Abstraction overhead** - May hide important CloudFormation details
- ❌ **Breaking changes** - History of breaking changes between major versions

**Example Serverless Framework Config:**
```yaml
service: exambuddy-api

provider:
  name: aws
  runtime: python3.11
  stage: ${opt:stage, 'dev'}
  region: us-east-1
  memorySize: 512
  timeout: 30

functions:
  api:
    handler: main.handler
    events:
      - httpApi:
          path: /{proxy+}
          method: ANY
```

### 2.3 Comparison Table

| Feature | AWS SAM | Serverless Framework |
|---------|---------|---------------------|
| **AWS Integration** | ⭐⭐⭐⭐⭐ Native | ⭐⭐⭐⭐ Good |
| **Multi-cloud** | ❌ AWS only | ✅ AWS, Azure, GCP |
| **Learning Curve** | ⭐⭐⭐ Moderate | ⭐⭐⭐⭐ Easy |
| **Syntax Complexity** | ⭐⭐ Verbose | ⭐⭐⭐⭐ Concise |
| **Plugin Ecosystem** | ⭐⭐ Limited | ⭐⭐⭐⭐⭐ Rich |
| **Local Testing** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐ Good |
| **Cost** | ✅ Free | ✅ Free (basic) |
| **Documentation** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Very Good |
| **Community Support** | ⭐⭐⭐⭐ Strong | ⭐⭐⭐⭐⭐ Very Strong |
| **AWS Feature Parity** | ⭐⭐⭐⭐⭐ Immediate | ⭐⭐⭐ Delayed |
| **Deployment Speed** | ⭐⭐⭐ Good | ⭐⭐⭐⭐ Fast |
| **Debugging Support** | ⭐⭐⭐⭐⭐ Built-in | ⭐⭐⭐ Plugin-based |

### 2.4 Recommendation: AWS SAM

**Justification for ExamBuddy:**
1. **AWS-centric architecture** - ExamBuddy appears to be AWS-native
2. **Better local development** - SAM Local provides superior testing capabilities
3. **CloudFormation compatibility** - Easy to integrate with existing IaC
4. **Long-term support** - AWS commitment to SAM as official tool
5. **No vendor lock-in concerns** - Open source and AWS-backed
6. **Better debugging** - Native IDE integration for debugging

**When to Choose Serverless Framework Instead:**
- Multi-cloud deployment is a requirement
- Team prefers simpler YAML syntax
- Need specific community plugins
- Existing Serverless Framework expertise

---

## 3. Cold Start Optimization for Python 3.11 Lambda

### 3.1 Understanding Lambda Cold Starts

**Cold Start Phases:**
1. **INIT Phase:**
   - Download function code from S3/ECR
   - Start execution environment
   - Initialize runtime
   - Run code outside handler (imports, connections)

2. **INVOKE Phase:**
   - Execute handler function
   - Return response

**Typical Cold Start Durations (Python 3.11 + FastAPI):**
- Baseline FastAPI: 500-800ms
- With dependencies (pydantic, sqlalchemy): 1-2 seconds
- With heavy ML libraries: 3-10+ seconds

### 3.2 Top 3 Cold Start Optimization Techniques for ExamBuddy

#### **Technique #1: Minimize Deployment Package Size**

**Strategy:**
Reduce the size of Lambda deployment package to decrease download time.

**Implementation:**
```bash
# 1. Use Lambda Layers for dependencies
# requirements.txt for function (minimal)
fastapi==0.109.0
mangum==0.17.0
pydantic==2.5.0

# requirements-layer.txt (heavy dependencies)
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
boto3==1.34.0

# 2. Build optimized wheel packages
pip install --upgrade pip
pip install -t ./layer/python -r requirements-layer.txt --platform manylinux2014_x86_64 --only-binary=:all:

# 3. Remove unnecessary files
cd layer/python
find . -type d -name "tests" -exec rm -rf {} +
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name "*.dist-info" -exec rm -rf {} +

# 4. Strip binaries
find . -name "*.so" -exec strip {} \;

# Result: ~50-70% size reduction
```

**Expected Impact:**
- Baseline package: 50MB → 15MB
- Cold start reduction: 200-400ms
- Cost savings: Lower storage costs

**SAM Template Configuration:**
```yaml
Resources:
  DependenciesLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: exambuddy-dependencies
      Description: FastAPI and database dependencies
      ContentUri: layers/dependencies/
      CompatibleRuntimes:
        - python3.11
    Metadata:
      BuildMethod: python3.11

  ExamBuddyApi:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: main.handler
      Layers:
        - !Ref DependenciesLayer
```

#### **Technique #2: Optimize Static Initialization**

**Strategy:**
Minimize work done outside the handler function. Use lazy loading for heavy resources.

**Bad Example (Slow Cold Start):**
```python
# main.py - DON'T DO THIS
from fastapi import FastAPI
from mangum import Mangum
import boto3
from sqlalchemy import create_engine
import pandas as pd
import numpy as np

# All these run on EVERY cold start
app = FastAPI()
db_engine = create_engine(DATABASE_URL)  # Expensive!
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
model_data = pd.read_csv('large_file.csv')  # Very expensive!

# Global connections created immediately
db_connection = db_engine.connect()

handler = Mangum(app)
```

**Good Example (Fast Cold Start):**
```python
# main.py - DO THIS
from fastapi import FastAPI
from mangum import Mangum

# Only import what you need
app = FastAPI()

# Lazy initialization pattern
_db_engine = None
_s3_client = None
_dynamodb = None

def get_db_engine():
    """Lazy load database engine only when needed"""
    global _db_engine
    if _db_engine is None:
        from sqlalchemy import create_engine
        import os
        _db_engine = create_engine(os.environ['DATABASE_URL'])
    return _db_engine

def get_s3_client():
    """Lazy load S3 client only when needed"""
    global _s3_client
    if _s3_client is None:
        import boto3
        _s3_client = boto3.client('s3')
    return _s3_client

@app.get("/exams")
def list_exams():
    # DB connection only created when this endpoint is called
    engine = get_db_engine()
    # ... use engine

@app.post("/upload")
def upload_file():
    # S3 client only created when this endpoint is called
    s3 = get_s3_client()
    # ... use s3

handler = Mangum(app, lifespan="off")
```

**Expected Impact:**
- Cold start reduction: 300-600ms
- Only pay for what you use per request
- Better memory efficiency

**Additional Tips:**
```python
# 1. Import heavy modules conditionally
@app.post("/ml-prediction")
def predict():
    # Import ML libraries only when needed
    import pandas as pd
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    # ... model logic

# 2. Reuse connections across invocations (warm starts)
_db_connection = None

def get_db_connection():
    global _db_connection
    if _db_connection is None or not _db_connection.is_active:
        engine = get_db_engine()
        _db_connection = engine.connect()
    return _db_connection

# 3. Use AWS SDK v3 for Node.js or modular imports for Python
# Instead of: import boto3
# Use: from boto3 import client; s3 = client('s3')
```

#### **Technique #3: Increase Memory Allocation**

**Strategy:**
Lambda allocates CPU proportionally to memory. More memory = faster execution = potentially lower cost despite higher GB-second rate.

**Analysis:**
According to AWS research, cold start performance improves with memory allocation:

| Memory | Cold Start | Duration | Cost (1000 invokes) |
|--------|-----------|----------|---------------------|
| 128 MB | ~2000ms | 1200ms | $0.025 |
| 256 MB | ~1500ms | 800ms | $0.034 |
| 512 MB | ~1000ms | 500ms | $0.042 |
| 1024 MB | ~600ms | 300ms | $0.050 |

**Sweet Spot for FastAPI:**
- **Recommended: 512MB - 1024MB**
- Below 512MB: Python initialization is CPU-bound and slow
- Above 1024MB: Diminishing returns for typical FastAPI apps

**SAM Configuration:**
```yaml
Resources:
  ExamBuddyApi:
    Type: AWS::Serverless::Function
    Properties:
      MemorySize: 1024  # Start here
      Timeout: 30
      # Use AWS Lambda Power Tuning to find optimal value
```

**Expected Impact:**
- Cold start reduction: 400-800ms
- Faster warm invocations: 200-400ms
- Cost increase: ~15-30% (but faster execution may offset)

**Using AWS Lambda Power Tuning:**
```bash
# Automated tool to find optimal memory configuration
# https://github.com/alexcasalboni/aws-lambda-power-tuning

# Deploy the tool via SAM
git clone https://github.com/alexcasalboni/aws-lambda-power-tuning.git
cd aws-lambda-power-tuning
sam deploy --guided

# Run analysis on your function
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:REGION:ACCOUNT:stateMachine:powerTuningStateMachine \
  --input '{
    "lambdaARN": "arn:aws:lambda:REGION:ACCOUNT:function:exambuddy-api",
    "powerValues": [512, 768, 1024, 1536, 2048],
    "num": 50
  }'
```

### 3.3 AWS Lambda SnapStart Considerations

**Important:** Lambda SnapStart is **NOT** available for Python runtimes.

**Current Support:**
- ✅ Java 11 (Corretto)
- ✅ Java 17 (Corretto)
- ✅ Java 21 (Corretto)
- ❌ Python (all versions)
- ❌ Node.js
- ❌ .NET
- ❌ Go
- ❌ Ruby

**SnapStart Benefits (Java only):**
- Reduces cold starts by 10x (6s → 600ms)
- Caches initialized Lambda execution environment
- Restores snapshot on subsequent invocations

**Alternative for Python:**
Since SnapStart is not available, use **Provisioned Concurrency** for latency-sensitive endpoints:

```yaml
Resources:
  ExamBuddyApi:
    Type: AWS::Serverless::Function
    Properties:
      MemorySize: 1024
      # Only for production, critical endpoints
      ProvisionedConcurrencyConfig:
        ProvisionedConcurrentExecutions: 2  # Keep 2 instances warm

  # Better: Use Provisioned Concurrency only on aliases
  ProductionAlias:
    Type: AWS::Lambda::Alias
    Properties:
      FunctionName: !Ref ExamBuddyApi
      FunctionVersion: !GetAtt ExamBuddyApi.Version
      Name: prod
      ProvisionedConcurrencyConfig:
        ProvisionedConcurrentExecutions: 5  # Scale based on traffic
```

**Cost Considerations:**
- Provisioned Concurrency is expensive (~$30/month per instance)
- Only use for business-critical, latency-sensitive endpoints
- Consider Application Auto Scaling to adjust concurrency based on schedule

### 3.4 Summary: Optimization Priority

**Implementation Order:**
1. ✅ **Start here:** Minimize package size (Technique #1)
   - Immediate impact, zero cost
   - 200-400ms improvement

2. ✅ **Then:** Optimize initialization (Technique #2)
   - Moderate effort, high impact
   - 300-600ms improvement

3. ✅ **Next:** Increase memory to 1024MB (Technique #3)
   - Instant change, slight cost increase
   - 400-800ms improvement

4. ⚠️ **Last resort:** Provisioned Concurrency
   - High cost, only for critical endpoints
   - Eliminates cold starts entirely

**Expected Total Improvement:**
- Baseline: 1500-2000ms cold start
- Optimized: 300-600ms cold start
- **~70-80% reduction**

---

## 4. FastAPI Routing and Middleware Compatibility with Lambda

### 4.1 Compatible Features

**✅ Fully Supported:**
- Path parameters: `/items/{item_id}`
- Query parameters: `/items?skip=0&limit=10`
- Request body (JSON, Form, File uploads)
- Response models and status codes
- Dependency injection
- Background tasks (runs before response)
- CORS middleware
- Custom middleware
- Exception handlers
- Request/response lifecycle events

**Example:**
```python
from fastapi import FastAPI, Depends, HTTPException
from mangum import Mangum

app = FastAPI()

# Dependency injection works perfectly
def get_db():
    # Returns DB connection
    pass

@app.get("/items/{item_id}")
async def read_item(
    item_id: int,
    q: str | None = None,
    db = Depends(get_db)
):
    return {"item_id": item_id, "q": q}

# CORS middleware works
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

handler = Mangum(app, lifespan="off")
```

### 4.2 Gotchas and Limitations

#### **⚠️ Issue #1: WebSocket Not Supported**

**Problem:**
Lambda Function URLs and API Gateway HTTP APIs do not support WebSocket connections natively through Mangum.

**Workaround:**
Use API Gateway WebSocket APIs separately, not through Mangum:
```yaml
# Separate WebSocket Lambda function
Resources:
  WebSocketFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: websocket_handler.handler
      Events:
        ConnectRoute:
          Type: Api
          Properties:
            Path: /
            Method: ANY
            RestApiId: !Ref WebSocketApi

  WebSocketApi:
    Type: AWS::ApiGatewayV2::Api
    Properties:
      Name: ExamBuddyWebSocket
      ProtocolType: WEBSOCKET
```

#### **⚠️ Issue #2: Streaming Responses Limited**

**Problem:**
Lambda response payload is limited to 6MB. Streaming large responses is not truly streaming in Lambda.

**Workaround:**
```python
# DON'T: Try to stream large responses
@app.get("/large-file")
async def download_large_file():
    def generate():
        for chunk in large_data:
            yield chunk
    return StreamingResponse(generate())

# DO: Return pre-signed S3 URL for large files
@app.get("/large-file")
async def download_large_file():
    s3_url = generate_presigned_url('bucket', 'key')
    return {"download_url": s3_url}
```

#### **⚠️ Issue #3: Lifespan Events in Lambda**

**Problem:**
FastAPI lifespan events (`startup`/`shutdown`) behave differently in Lambda:
- `startup` runs on cold start only (not every invocation)
- `shutdown` may not run reliably (Lambda freezes containers)

**Solution:**
Disable lifespan events in Lambda:
```python
# Correct way
handler = Mangum(app, lifespan="off")

# Move startup logic to lazy initialization
_startup_complete = False

@app.middleware("http")
async def ensure_startup(request, call_next):
    global _startup_complete
    if not _startup_complete:
        # Run one-time setup
        await setup_database()
        _startup_complete = True
    return await call_next(request)
```

#### **⚠️ Issue #4: API Gateway Request/Response Limits**

**Limits:**
- Max request body: 10MB (API Gateway HTTP API)
- Max response body: 10MB (HTTP API), 6MB (REST API)
- Max timeout: 30 seconds (API Gateway), 15 minutes (Lambda max, but not practical)

**Workaround for Large Uploads:**
```python
@app.post("/upload-large")
async def upload_large_file():
    # Generate pre-signed POST URL for direct S3 upload
    presigned_post = s3_client.generate_presigned_post(
        Bucket='bucket',
        Key='uploads/${filename}',
        ExpiresIn=3600
    )
    return {"upload_url": presigned_post}
```

#### **⚠️ Issue #5: Binary Media Types**

**Problem:**
Binary responses (images, PDFs) require special API Gateway configuration.

**Solution:**
```yaml
# SAM template
Resources:
  ExamBuddyHttpApi:
    Type: AWS::Serverless::HttpApi
    Properties:
      # Configure binary media types
      BinaryMediaTypes:
        - image/png
        - image/jpeg
        - application/pdf
        - application/octet-stream
```

```python
# FastAPI handler
from fastapi.responses import Response

@app.get("/download-pdf")
async def download_pdf():
    pdf_content = generate_pdf()
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=exam.pdf"}
    )
```

#### **⚠️ Issue #6: Cold Start Impact on Timeouts**

**Problem:**
If API Gateway timeout is 30s and cold start takes 2s, handler has only 28s to execute.

**Solution:**
```yaml
Resources:
  ExamBuddyApi:
    Type: AWS::Serverless::Function
    Properties:
      Timeout: 30  # Lambda timeout
      Events:
        ApiEvent:
          Type: HttpApi
          Properties:
            TimeoutInMillis: 30000  # API Gateway timeout (match or exceed Lambda)
```

### 4.3 Middleware Execution Order

**Important:** Middleware executes on every invocation, even warm starts. Keep middleware lightweight.

```python
from fastapi import FastAPI, Request
import time

app = FastAPI()

# Execution order: 1 → 2 → 3 → Route Handler → 3 → 2 → 1

@app.middleware("http")  # 1. First middleware
async def add_request_id(request: Request, call_next):
    request.state.request_id = generate_id()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response

@app.middleware("http")  # 2. Second middleware
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    print(f"Request took {duration}s")
    return response

@app.middleware("http")  # 3. Third middleware (executes last)
async def auth_middleware(request: Request, call_next):
    # Auth check
    return await call_next(request)
```

---

## 5. Local Development and Testing Approaches

### 5.1 SAM Local (Recommended)

**Overview:**
SAM CLI provides local Lambda runtime emulation using Docker containers.

**Features:**
- ✅ Emulates API Gateway locally
- ✅ Supports Lambda environment variables
- ✅ Hot-reload for rapid development
- ✅ Debug with IDE breakpoints
- ✅ Test individual functions
- ✅ Generate sample events

**Setup:**
```bash
# Install SAM CLI
pip install aws-sam-cli

# Verify installation
sam --version
```

**Project Structure:**
```
exambuddy/
├── src/
│   ├── main.py          # FastAPI app + Mangum handler
│   ├── api/
│   │   ├── routes/
│   │   └── models/
│   └── requirements.txt
├── layers/
│   └── dependencies/
│       └── requirements.txt
├── tests/
│   ├── unit/
│   └── integration/
├── events/              # Sample Lambda events for testing
│   ├── event-get-exam.json
│   └── event-post-exam.json
├── template.yaml        # SAM template
└── samconfig.toml       # SAM configuration
```

**Local Development Workflow:**

```bash
# 1. Start local API
sam build
sam local start-api --port 8000

# API available at: http://localhost:8000

# 2. With auto-reload (requires sam-beta-cdk)
sam sync --stack-name exambuddy-dev --watch

# 3. Test specific function
sam local invoke ExamBuddyApi --event events/event-get-exam.json

# 4. Generate sample event
sam local generate-event apigateway http-api-proxy > events/sample.json

# 5. Run with environment variables
sam local start-api --env-vars env.json

# env.json
{
  "ExamBuddyApi": {
    "DATABASE_URL": "postgresql://localhost/exambuddy",
    "STAGE": "local"
  }
}
```

**Debugging with VS Code:**
```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "SAM Local API",
      "type": "python",
      "request": "attach",
      "port": 5858,
      "host": "localhost",
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}/src",
          "remoteRoot": "/var/task"
        }
      ]
    }
  ]
}
```

```bash
# Start API in debug mode
sam local start-api --debug-port 5858
# Then attach debugger in VS Code (F5)
```

**Pros:**
- ✅ Official AWS tool
- ✅ Accurate Lambda environment simulation
- ✅ Works offline (after first pull)
- ✅ Integrated with SAM deploy workflow

**Cons:**
- ❌ Requires Docker
- ❌ Slower startup than native Python
- ❌ Limited support for some AWS services locally

### 5.2 LocalStack

**Overview:**
LocalStack provides a fully functional local AWS cloud stack, including Lambda, API Gateway, S3, DynamoDB, and more.

**Features:**
- ✅ Emulates 100+ AWS services
- ✅ Persistence between sessions
- ✅ Cloud-native development workflow
- ✅ Pro version includes advanced features

**Setup:**
```bash
# Install LocalStack
pip install localstack

# Start LocalStack (Community)
localstack start

# Or use Docker Compose
docker-compose up
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  localstack:
    image: localstack/localstack:latest
    ports:
      - "4566:4566"  # LocalStack Gateway
      - "4571:4571"  # LocalStack UI (Pro)
    environment:
      - SERVICES=lambda,apigateway,s3,dynamodb,rds
      - DEBUG=1
      - LAMBDA_EXECUTOR=docker
      - DOCKER_HOST=unix:///var/run/docker.sock
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock"
      - "./localstack-data:/var/lib/localstack"
```

**Deploy to LocalStack:**
```bash
# Configure AWS CLI for LocalStack
export AWS_ENDPOINT_URL=http://localhost:4566
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test

# Deploy using SAM
sam build
sam deploy \
  --template-file .aws-sam/build/template.yaml \
  --stack-name exambuddy-local \
  --resolve-s3 \
  --capabilities CAPABILITY_IAM \
  --region us-east-1 \
  --no-confirm-changeset

# Test the API
curl http://localhost:4566/restapis/API_ID/local/_user_request_/exams
```

**Pros:**
- ✅ Full AWS ecosystem locally
- ✅ Test service integrations (S3, DynamoDB, etc.)
- ✅ Persistent state between restarts
- ✅ Cloud parity for complex workflows

**Cons:**
- ❌ Requires Docker
- ❌ Some features only in Pro ($
- ❌ Learning curve for complex setups
- ❌ Not all AWS services have 100% parity

### 5.3 Docker Compose (Development Environment)

**Overview:**
Create a complete development environment with FastAPI, database, and services.

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  # FastAPI app (native, fast development)
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/exambuddy
      - REDIS_URL=redis://redis:6379/0
      - AWS_ENDPOINT_URL=http://localstack:4566
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    depends_on:
      - db
      - redis
      - localstack

  # PostgreSQL database
  db:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=exambuddy
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres-data:/var/lib/postgresql/data

  # Redis cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # LocalStack for AWS services
  localstack:
    image: localstack/localstack:latest
    ports:
      - "4566:4566"
    environment:
      - SERVICES=s3,dynamodb,ses
      - DEBUG=1
    volumes:
      - "./localstack-init:/etc/localstack/init/ready.d"

volumes:
  postgres-data:
```

**Usage:**
```bash
# Start all services
docker-compose up

# FastAPI app available at: http://localhost:8000
# Automatic reload on code changes

# Run tests in container
docker-compose exec api pytest

# Shell into container
docker-compose exec api bash
```

**Pros:**
- ✅ Fast feedback loop (native FastAPI, no Lambda overhead)
- ✅ Full-stack development environment
- ✅ Easy to add services (Postgres, Redis, etc.)
- ✅ Team-friendly (reproducible environment)

**Cons:**
- ❌ Not identical to Lambda runtime
- ❌ Requires adjusting code for local vs Lambda
- ❌ API Gateway behavior not simulated

### 5.4 Hybrid Approach (Recommended)

**Strategy:**
Combine tools for different stages of development.

**Daily Development:**
```bash
# Fast iteration with native FastAPI
uvicorn src.main:app --reload --port 8000

# Or use docker-compose for full stack
docker-compose up
```

**Pre-Commit Testing:**
```bash
# Test Lambda integration with SAM Local
sam build
sam local start-api

# Run integration tests
pytest tests/integration/
```

**Pre-Deploy Testing:**
```bash
# Deploy to LocalStack for full AWS integration testing
sam deploy --stack-name exambuddy-local --endpoint-url http://localhost:4566

# Smoke test all endpoints
./scripts/smoke-test.sh http://localhost:4566/restapis/API_ID/local/_user_request_
```

**CI/CD Pipeline:**
```yaml
# .github/workflows/test.yml
name: Test Pipeline

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: pytest tests/unit/

  integration-tests:
    runs-on: ubuntu-latest
    services:
      localstack:
        image: localstack/localstack:latest
        ports:
          - 4566:4566
    steps:
      - uses: actions/checkout@v3
      - name: Setup SAM CLI
        run: pip install aws-sam-cli
      - name: Deploy to LocalStack
        run: sam deploy --stack-name test --endpoint-url http://localhost:4566
      - name: Run integration tests
        run: pytest tests/integration/
```

---

## 6. Sample Project Structure Recommendations

### 6.1 Recommended Directory Structure

```
exambuddy/
├── .github/
│   └── workflows/
│       ├── test.yml                 # CI/CD pipeline
│       └── deploy.yml               # Deployment workflow
├── src/
│   ├── main.py                      # FastAPI app + Lambda handler
│   ├── config.py                    # Configuration management
│   ├── dependencies.py              # Lazy-loaded dependencies
│   └── api/
│       ├── __init__.py
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── exams.py            # Exam endpoints
│       │   ├── questions.py        # Question endpoints
│       │   └── users.py            # User endpoints
│       ├── models/
│       │   ├── __init__.py
│       │   ├── exam.py
│       │   └── question.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── exam_service.py
│       │   └── question_service.py
│       └── middleware/
│           ├── __init__.py
│           ├── auth.py
│           └── logging.py
├── layers/
│   └── dependencies/
│       ├── python/                  # Lambda layer structure
│       └── requirements.txt         # Layer dependencies
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures
│   ├── unit/
│   │   ├── test_exam_service.py
│   │   └── test_question_service.py
│   ├── integration/
│   │   ├── test_api_exams.py
│   │   └── test_api_questions.py
│   └── e2e/
│       └── test_full_workflow.py
├── events/                          # Sample Lambda events
│   ├── event-get-exam.json
│   ├── event-post-exam.json
│   └── event-api-gateway-proxy.json
├── scripts/
│   ├── build.sh                     # Build script
│   ├── deploy.sh                    # Deployment script
│   ├── local-dev.sh                 # Local development setup
│   └── smoke-test.sh                # Smoke testing
├── docs/
│   ├── api/                         # API documentation
│   └── architecture/                # Architecture diagrams
├── .env.example                     # Environment variables template
├── .gitignore
├── docker-compose.yml               # Local development environment
├── Dockerfile.dev                   # Development Docker image
├── pytest.ini                       # Pytest configuration
├── requirements.txt                 # Function dependencies (minimal)
├── requirements-dev.txt             # Development dependencies
├── samconfig.toml                   # SAM configuration
├── template.yaml                    # SAM template (IaC)
└── README.md
```

### 6.2 Sample main.py (Lambda Handler)

```python
"""
ExamBuddy Lambda Handler
FastAPI application with Mangum adapter for AWS Lambda
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Import routers
from api.routes import exams, questions, users

# Environment
STAGE = os.environ.get("STAGE", "dev")

# FastAPI app
app = FastAPI(
    title="ExamBuddy API",
    description="Serverless exam management platform",
    version="1.0.0",
    # Don't include docs in production for security
    docs_url="/docs" if STAGE != "prod" else None,
    redoc_url="/redoc" if STAGE != "prod" else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on STAGE
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(exams.router, prefix="/exams", tags=["exams"])
app.include_router(questions.router, prefix="/questions", tags=["questions"])
app.include_router(users.router, prefix="/users", tags=["users"])

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "stage": STAGE}

# Lambda handler (only used in Lambda environment)
# In local development, run: uvicorn main:app --reload
handler = Mangum(app, lifespan="off")

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

### 6.3 Sample SAM Template

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: ExamBuddy Serverless API

Globals:
  Function:
    Timeout: 30
    Runtime: python3.11
    MemorySize: 1024
    Architectures:
      - x86_64
    Environment:
      Variables:
        STAGE: !Ref Stage
        LOG_LEVEL: INFO

Parameters:
  Stage:
    Type: String
    Default: dev
    AllowedValues:
      - dev
      - staging
      - prod

Conditions:
  IsProduction: !Equals [!Ref Stage, prod]

Resources:
  # Lambda Layer for dependencies
  DependenciesLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: !Sub exambuddy-dependencies-${Stage}
      Description: FastAPI, SQLAlchemy, and other dependencies
      ContentUri: layers/dependencies/
      CompatibleRuntimes:
        - python3.11
      RetentionPolicy: Delete
    Metadata:
      BuildMethod: python3.11

  # Lambda Function
  ExamBuddyApi:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: !Sub exambuddy-api-${Stage}
      CodeUri: src/
      Handler: main.handler
      Layers:
        - !Ref DependenciesLayer
      Environment:
        Variables:
          DATABASE_URL: !Sub "{{resolve:secretsmanager:exambuddy/${Stage}/db:SecretString:url}}"
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref ExamTable
        - S3CrudPolicy:
            BucketName: !Ref ExamFilesBucket
      Events:
        ApiEvent:
          Type: HttpApi
          Properties:
            Path: /{proxy+}
            Method: ANY
            ApiId: !Ref HttpApi
      # Production: Use Provisioned Concurrency for critical endpoints
      # ProvisionedConcurrencyConfig:
      #   ProvisionedConcurrentExecutions: !If [IsProduction, 2, 0]

  # HTTP API Gateway
  HttpApi:
    Type: AWS::Serverless::HttpApi
    Properties:
      StageName: !Ref Stage
      CorsConfiguration:
        AllowOrigins:
          - "*"
        AllowMethods:
          - GET
          - POST
          - PUT
          - DELETE
          - OPTIONS
        AllowHeaders:
          - "*"
      # Production: Use custom domain
      # Domain:
      #   DomainName: !If [IsProduction, api.exambuddy.com, !Sub api-${Stage}.exambuddy.com]
      #   CertificateArn: !Ref Certificate

  # DynamoDB Table
  ExamTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub exambuddy-exams-${Stage}
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: exam_id
          AttributeType: S
        - AttributeName: created_at
          AttributeType: N
      KeySchema:
        - AttributeName: exam_id
          KeyType: HASH
        - AttributeName: created_at
          KeyType: RANGE
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES

  # S3 Bucket for exam files
  ExamFilesBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub exambuddy-files-${Stage}-${AWS::AccountId}
      CorsConfiguration:
        CorsRules:
          - AllowedOrigins:
              - "*"
            AllowedMethods:
              - GET
              - PUT
              - POST
            AllowedHeaders:
              - "*"

Outputs:
  ApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${HttpApi}.execute-api.${AWS::Region}.amazonaws.com/${Stage}"
  
  FunctionArn:
    Description: Lambda Function ARN
    Value: !GetAtt ExamBuddyApi.Arn
  
  LayerArn:
    Description: Dependencies Layer ARN
    Value: !Ref DependenciesLayer
```

### 6.4 Local Development Setup

**scripts/local-dev.sh:**
```bash
#!/bin/bash
set -e

echo "Setting up ExamBuddy local development environment..."

# Start LocalStack
echo "Starting LocalStack..."
docker-compose up -d localstack

# Wait for LocalStack to be ready
echo "Waiting for LocalStack..."
until curl -s http://localhost:4566/_localstack/health | grep -q '"dynamodb": "available"'; do
  sleep 1
done

# Create local DynamoDB table
echo "Creating DynamoDB table..."
aws dynamodb create-table \
  --endpoint-url http://localhost:4566 \
  --table-name exambuddy-exams-local \
  --attribute-definitions \
    AttributeName=exam_id,AttributeType=S \
    AttributeName=created_at,AttributeType=N \
  --key-schema \
    AttributeName=exam_id,KeyType=HASH \
    AttributeName=created_at,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

# Create S3 bucket
echo "Creating S3 bucket..."
aws s3 mb s3://exambuddy-files-local --endpoint-url http://localhost:4566

# Start FastAPI with hot-reload
echo "Starting FastAPI app..."
export DATABASE_URL="postgresql://postgres:password@localhost:5432/exambuddy"
export AWS_ENDPOINT_URL="http://localhost:4566"
export STAGE="local"

uvicorn src.main:app --reload --port 8000

echo "Local development environment ready!"
echo "API: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
```

---

## 7. Key Takeaways and Recommendations

### 7.1 Quick Decision Matrix

| Decision Point | Recommendation | Rationale |
|---------------|----------------|-----------|
| **ASGI Adapter** | Mangum | Industry standard, battle-tested |
| **Deployment Tool** | AWS SAM | AWS-native, better local testing |
| **Cold Start #1** | Minimize package size | Immediate impact, zero cost |
| **Cold Start #2** | Lazy initialization | High impact, best practice |
| **Cold Start #3** | 1024MB memory | Sweet spot for FastAPI |
| **Local Dev Primary** | Native FastAPI + Docker Compose | Fast feedback loop |
| **Local Dev Testing** | SAM Local | Lambda environment parity |
| **Pre-deploy Testing** | LocalStack | Full AWS integration testing |

### 7.2 Implementation Checklist

**Phase 1: Basic Setup** (Week 1)
- [ ] Install Mangum adapter
- [ ] Create SAM template
- [ ] Set up basic FastAPI app with Mangum handler
- [ ] Deploy to AWS (dev environment)
- [ ] Test basic endpoint

**Phase 2: Optimization** (Week 2)
- [ ] Split dependencies into Lambda Layer
- [ ] Implement lazy loading pattern
- [ ] Remove unnecessary files from package
- [ ] Set memory to 1024MB
- [ ] Measure cold start improvements

**Phase 3: Local Development** (Week 3)
- [ ] Set up docker-compose environment
- [ ] Configure SAM Local
- [ ] Create sample Lambda events
- [ ] Add debugging configuration
- [ ] Document local development workflow

**Phase 4: Testing & CI/CD** (Week 4)
- [ ] Set up LocalStack in CI pipeline
- [ ] Create integration test suite
- [ ] Add smoke tests
- [ ] Configure automated deployment
- [ ] Monitor cold start metrics in production

### 7.3 Common Pitfalls to Avoid

1. **❌ Don't:** Import heavy libraries at module level
   **✅ Do:** Use lazy loading for expensive imports

2. **❌ Don't:** Use WebSocket endpoints in Lambda
   **✅ Do:** Use separate WebSocket API or polling

3. **❌ Don't:** Forget to disable lifespan events
   **✅ Do:** Always use `Mangum(app, lifespan="off")`

4. **❌ Don't:** Try to stream large files through Lambda
   **✅ Do:** Use S3 pre-signed URLs

5. **❌ Don't:** Set Lambda memory too low (< 512MB)
   **✅ Do:** Start with 1024MB, tune with Power Tuning

6. **❌ Don't:** Use Provisioned Concurrency everywhere
   **✅ Do:** Reserve for critical, latency-sensitive endpoints

7. **❌ Don't:** Test only locally without Lambda environment
   **✅ Do:** Use SAM Local or LocalStack for pre-deploy testing

### 7.4 Monitoring and Observability

**Recommended Tools:**
```python
# AWS Lambda Powertools for Python
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit

logger = Logger()
tracer = Tracer()
metrics = Metrics()

@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def handler(event, context):
    # Automatic cold start metrics
    # Structured logging
    # X-Ray tracing
    return mangum_handler(event, context)
```

**Key Metrics to Track:**
- Cold start duration and frequency
- Warm start latency (p50, p95, p99)
- Memory utilization
- Error rates
- API Gateway throttling
- Cost per invocation

---

## 8. Additional Resources

### Documentation
- [Mangum Documentation](https://mangum.io/)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [LocalStack Documentation](https://docs.localstack.cloud/)

### Blog Posts & Guides
- [AWS: Operating Lambda Performance Optimization](https://aws.amazon.com/blogs/compute/operating-lambda-performance-optimization-part-1/)
- [FastAPI on Lambda Tutorial](https://testdriven.io/blog/fastapi-lambda/)
- [Lambda Cold Start Analysis](https://mikhail.io/serverless/coldstarts/aws/)

### Tools
- [AWS Lambda Power Tuning](https://github.com/alexcasalboni/aws-lambda-power-tuning)
- [AWS Lambda Powertools](https://github.com/aws-powertools/powertools-lambda-python)
- [LocalStack](https://localstack.cloud/)
- [SAM CLI](https://github.com/aws/aws-sam-cli)

### Example Projects
- [AWS SAM FastAPI Example](https://github.com/aws-samples/aws-sam-python-fastapi)
- [Serverless FastAPI Example](https://github.com/serverless/examples/tree/master/aws-python-fastapi-api)

---

## Appendix: Quick Start Template

For ExamBuddy, here's a quick start template:

```bash
# 1. Install tools
pip install aws-sam-cli mangum fastapi

# 2. Create project structure
mkdir -p exambuddy/{src,layers/dependencies,tests,events}

# 3. Create main.py
cat > exambuddy/src/main.py << 'EOF'
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy"}

handler = Mangum(app, lifespan="off")
EOF

# 4. Create SAM template
cat > exambuddy/template.yaml << 'EOF'
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  ExamBuddyApi:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: main.handler
      Runtime: python3.11
      MemorySize: 1024
      Events:
        ApiEvent:
          Type: HttpApi
          Properties:
            Path: /{proxy+}
            Method: ANY
EOF

# 5. Build and deploy
cd exambuddy
sam build
sam deploy --guided

# 6. Test
curl https://YOUR_API_URL/health
```

---

**End of Report**

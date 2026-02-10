# ExamBuddy Backend

Python FastAPI backend for ExamBuddy Online Exam Center Platform.

## Features

- **FastAPI Framework**: High-performance async API with automatic OpenAPI documentation
- **AWS Lambda Ready**: Mangum adapter for serverless deployment
- **DynamoDB**: Single-table design for scalable data storage
- **S3 Integration**: PDF uploads and result exports with presigned URLs
- **Cognito Auth**: AWS Cognito JWT token verification
- **PDF Processing**: pypdf + pdfplumber for question extraction
- **Report Generation**: CSV and PDF result exports

## Prerequisites

- Python 3.11+
- Docker & Docker Compose (for local development)
- AWS SAM CLI (for Lambda testing)
- AWS Account with configured credentials

## Local Development Setup

### 1. Environment Variables

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` with your AWS credentials and configuration.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run with Docker Compose

Start all services (backend, DynamoDB local, LocalStack S3):

```bash
docker-compose up
```

Backend API will be available at: `http://localhost:8000`

### 4. Run Locally (without Docker)

```bash
uvicorn src.main:app --reload --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Project Structure

```
backend/
├── src/
│   ├── api/              # API endpoint routers
│   ├── models/           # Pydantic data models
│   ├── services/         # Business logic services
│   ├── middleware/       # Auth & error handling middleware
│   ├── database/         # DynamoDB & S3 clients
│   ├── config.py         # Environment configuration
│   └── main.py           # FastAPI app & Mangum handler
├── tests/                # Pytest test suite
├── requirements.txt      # Python dependencies
├── Dockerfile            # Local development container
└── template.yaml         # AWS SAM deployment template
```

## Testing

Run tests with pytest:

```bash
pytest tests/ -v
```

With coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

## AWS SAM Local Testing

Test Lambda function locally:

```bash
sam build
sam local start-api --port 8000
```

## Deployment

Deploy to AWS Lambda:

```bash
sam build
sam deploy --guided
```

## Environment Variables

See `.env.example` for required variables:
- AWS credentials and region
- DynamoDB table name
- S3 bucket names
- Cognito User Pool configuration
- JWT secret (local dev fallback)

## Code Quality

Format with Black:
```bash
black src/
```

Lint with Flake8:
```bash
flake8 src/
```

Type check with MyPy:
```bash
mypy src/
```

## Performance Targets

- Cold start: <2s (1024MB memory)
- PDF parsing: <3s (50 Q&A)
- Question loading: <1s
- Answer submission: <500ms
- Dashboard generation: <2s (100 attempts)

## License

Proprietary - ExamBuddy Platform

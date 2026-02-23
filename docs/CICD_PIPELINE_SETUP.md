# ExamBuddy CI/CD Pipeline Setup Guide

## Overview
This guide sets up a complete CI/CD pipeline for automated testing, building, and deployment to AWS.

---

## Prerequisites

### AWS Account Setup (Admin Required ⚠️)

Before proceeding, an **AWS account administrator** must:

1. **Create IAM Role for CI/CD**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "AWS": "arn:aws:iam::887863153274:user/github-actions-deployer"
         },
         "Action": "sts:AssumeRole"
       }
     ]
   }
   ```
   - Role Name: `ExamBuddyCIPipelineRole`
   - Attach Policy: `AdministratorAccess`

2. **Create GitHub Actions OIDC Provider** (for GitHub-based CI/CD)
   ```bash
   aws iam create-open-id-connect-provider \
     --url "https://token.actions.githubusercontent.com" \
     --client-id-list "sts.amazonaws.com" \
     --thumbprint-list "6938fd4d98bab03faadb97b34396831e3780aea1"
   ```

3. **Grant IAM Permissions to github-actions-deployer user**:
   - `iam:PassRole`
   - `iam:CreateRole`
   - `iam:PutRolePolicy`
   - `lambda:*`
   - `apigateway:*`
   - `cloudformation:*`
   - `s3:*`
   - `dynamodb:*`
   - `logs:*`

---

## Step 1: Create GitHub Actions Workflow

### 1.1 Create workflow file
```bash
mkdir -p .github/workflows
```

### 1.2 Create deployment workflow
**File: `.github/workflows/deploy.yml`**

```yaml
name: Deploy ExamBuddy

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

env:
  AWS_REGION: eu-north-1
  DOCKER_IMAGE: exambuddy-deploy:latest

jobs:
  test:
    runs-on: ubuntu-latest
    name: Test Backend
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        working-directory: backend
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run tests
        working-directory: backend
        run: |
          python -m pytest tests/ -v --cov=src

  build:
    runs-on: ubuntu-latest
    name: Build Frontend & Backend
    needs: test
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Build Frontend
        working-directory: frontend
        run: |
          npm install
          npm run build
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: frontend-build
          path: frontend/dist

  deploy:
    runs-on: ubuntu-latest
    name: Deploy to AWS
    needs: build
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: arn:aws:iam::887863153274:role/ExamBuddyCIPipelineRole
          aws-region: eu-north-1
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install SAM CLI
        run: |
          pip install aws-sam-cli boto3
      
      - name: Build SAM application
        working-directory: backend
        run: |
          sam build
      
      - name: Deploy SAM application
        working-directory: backend
        run: |
          sam deploy \
            --no-confirm-changeset \
            --stack-name exambuddy-staging \
            --s3-prefix exambuddy-staging \
            --capabilities CAPABILITY_IAM \
            --region eu-north-1 \
            --parameter-overrides \
              DynamoDBTableName=exambuddy-main \
              S3PdfsBucket=exambuddy-pdfs \
              S3ExportsBucket=exambuddy-exports \
              CognitoUserPoolId=${{ secrets.COGNITO_USER_POOL_ID }} \
              CognitoClientId=${{ secrets.COGNITO_CLIENT_ID }} \
              JWTSecret=${{ secrets.JWT_SECRET }}
      
      - name: Get API URL
        working-directory: backend
        run: |
          API_URL=$(aws cloudformation describe-stacks \
            --stack-name exambuddy-staging \
            --query 'Stacks[0].Outputs[?OutputKey==`ExamBuddyApiEndpoint`].OutputValue' \
            --output text \
            --region eu-north-1)
          echo "DEPLOYMENT_URL=$API_URL" >> $GITHUB_ENV
          echo "✅ API Deployed: $API_URL"
```

---

## Step 2: Add GitHub Secrets

Navigate to **GitHub → Settings → Secrets and variables → Actions** and add:

| Secret Name | Value | Description |
|---|---|---|
| `COGNITO_USER_POOL_ID` | (from AWS) | Cognito User Pool ID |
| `COGNITO_CLIENT_ID` | (from AWS) | Cognito App Client ID |
| `JWT_SECRET` | (generate: `openssl rand -base64 32`) | JWT signing secret |

---

## Step 3: Create SAM Configuration

**File: `backend/samconfig.toml`**

```toml
version = 0.1

[default]
[default.deploy]
[default.deploy.parameters]
stack_name = "exambuddy-staging"
s3_bucket = "aws-sam-cli-managed-default-samclisourcebucket-aw1qziuara82"
s3_prefix = "exambuddy-staging"
region = "eu-north-1"
confirm_changeset = false
capabilities = "CAPABILITY_IAM"
parameter_overrides = """
DynamoDBTableName=exambuddy-main
S3PdfsBucket=exambuddy-pdfs
S3ExportsBucket=exambuddy-exports
CognitoUserPoolId=temp
CognitoClientId=temp
JWTSecret=temp
"""
```

---

## Step 4: Local Testing Pipeline

### 4.1 Run backend tests locally
```bash
cd backend
python -m pytest tests/ -v --cov=src
```

### 4.2 Run frontend tests locally
```bash
cd frontend
npm run test
```

### 4.3 Run local SAM build
```bash
cd backend
sam build
```

### 4.4 Run local SAM invocation
```bash
cd backend
sam local invoke ExamBuddyFunction -e events/event.json
```

---

## Step 5: Manual Deployment (Until Pipeline Ready)

### 5.1 Docker-based deployment
```bash
# Build Docker image
docker build -f Dockerfile.deploy -t exambuddy-deploy:latest .

# Run SAM build
docker run -it \
  -v $(pwd):/app \
  -w /app/backend \
  exambuddy-deploy:latest \
  sam build

# Run SAM deploy (guided)
docker run -it \
  -v $(pwd):/app \
  -v $HOME/.aws:/root/.aws \
  -w /app/backend \
  exambuddy-deploy:latest \
  sam deploy --guided
```

---

## Step 6: Deployment Checklist

Before deploying to production, verify:

- [ ] All tests passing (`pytest`, `npm test`)
- [ ] Frontend build completes without errors
- [ ] SAM build succeeds
- [ ] AWS credentials configured
- [ ] GitHub secrets added
- [ ] IAM role has proper permissions
- [ ] DynamoDB table exists (or will be created)
- [ ] S3 buckets for PDFs and exports created
- [ ] Cognito User Pool setup complete
- [ ] API Gateway endpoints accessible

---

## Step 7: Monitoring Deployments

### View CloudFormation events
```bash
aws cloudformation describe-stack-events \
  --stack-name exambuddy-staging \
  --query 'StackEvents[0:10]'
```

### View Lambda logs
```bash
aws logs tail /aws/lambda/ExamBuddyFunction --follow
```

### View API Gateway metrics
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

---

## Troubleshooting

### Issue: "User is not authorized to perform: iam:CreateRole"
**Solution**: Admin must grant `iam:CreateRole` permission or create role pre-emptively.

### Issue: "Waiting for changeset to be created..." times out
**Solution**: 
```bash
# Cancel changeset
aws cloudformation cancel-update-stack --stack-name exambuddy-staging
```

### Issue: Lambda function timeout
**Solution**: Increase timeout in `template.yaml`:
```yaml
Timeout: 60  # Increase from 30
```

### Issue: S3 bucket doesn't exist
**Solution**: Create buckets first:
```bash
aws s3 mb s3://exambuddy-pdfs-dev-887863153274 --region eu-north-1
aws s3 mb s3://exambuddy-exports-dev-887863153274 --region eu-north-1
```

---

## Next Steps

1. **Get admin approval** for IAM role and GitHub OIDC provider
2. **Add GitHub workflow file** to `.github/workflows/deploy.yml`
3. **Configure GitHub secrets**
4. **Test pipeline** with a pull request
5. **Monitor first production deployment**
6. **Setup CloudWatch alarms** for monitoring
7. **Document API endpoints** in README

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Repository                         │
│                   (main branch push)                          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │    GitHub Actions Workflow             │
        │  ┌──────────────────────────────────┐  │
        │  │ 1. Run Tests (Backend & Frontend)│  │
        │  └──────────────────────────────────┘  │
        │  ┌──────────────────────────────────┐  │
        │  │ 2. Build (Frontend + Docker)     │  │
        │  └──────────────────────────────────┘  │
        │  ┌──────────────────────────────────┐  │
        │  │ 3. SAM Build                     │  │
        │  └──────────────────────────────────┘  │
        │  ┌──────────────────────────────────┐  │
        │  │ 4. SAM Deploy → AWS              │  │
        │  └──────────────────────────────────┘  │
        └────────────────────┬───────────────────┘
                             │
                    ┌────────▼────────┐
                    │  AWS Account    │
                    │ (887863153274)  │
                    │                 │
                    │ ┌─────────────┐ │
                    │ │ Lambda      │ │
                    │ │ Functions   │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │ API Gateway │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │ DynamoDB    │ │
                    │ └─────────────┘ │
                    │ ┌─────────────┐ │
                    │ │ S3 Buckets  │ │
                    │ └─────────────┘ │
                    └─────────────────┘
```

---

## Contact

For AWS IAM setup assistance, contact your **AWS Account Administrator**.


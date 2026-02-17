# ExamBuddy CI/CD Pipeline - Quick Start Guide

## 📋 What We've Setup

Your project now has a **complete CI/CD pipeline** with:

1. ✅ **GitHub Actions Workflow** - Auto-test, build, and deploy on push to `main`
2. ✅ **SAM Configuration** - Ready for AWS Lambda deployment
3. ✅ **Docker Support** - Consistent build environment
4. ✅ **Staging Stack** - Separate AWS environment for testing

---

## 🚀 Getting Started (5 Steps)

### Step 1: Add GitHub Secrets

Go to your GitHub repo → **Settings → Secrets and variables → Actions**

Add these secrets:
| Secret Name | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | (Your AWS Access Key) |
| `AWS_SECRET_ACCESS_KEY` | (Your AWS Secret Key) |
| `COGNITO_USER_POOL_ID` | (Your Cognito Pool ID or temp value) |
| `COGNITO_CLIENT_ID` | (Your Cognito Client ID or temp value) |
| `JWT_SECRET` | Generate: `openssl rand -base64 32` |

### Step 2: Create Required AWS Resources

Before first deployment, create these resources:

```bash
# Create S3 buckets
aws s3 mb s3://exambuddy-pdfs --region eu-north-1
aws s3 mb s3://exambuddy-exports --region eu-north-1

# Create DynamoDB table
aws dynamodb create-table \
  --table-name exambuddy-main \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region eu-north-1
```

### Step 3: Commit & Push Workflow

```bash
git add .github/workflows/deploy.yml backend/samconfig.toml
git commit -m "feat: add CI/CD pipeline with GitHub Actions"
git push origin main
```

### Step 4: Monitor GitHub Actions

- Go to **Actions** tab in your GitHub repo
- Watch the workflow execute
- Check logs if any step fails

### Step 5: Get Your API Endpoint

Once deployment succeeds:
- Check the workflow summary for API URL
- Update `frontend/src/config.js` with the endpoint
- Deploy frontend separately or trigger another pipeline run

---

## 🔄 Pipeline Stages Explained

### Stage 1: Test
```
✓ Install Python dependencies
✓ Run backend tests
```
**Runs on**: Every push & pull request

### Stage 2: Build Frontend
```
✓ Install Node.js dependencies
✓ Build React app (npm run build)
✓ Upload dist/ artifacts
```
**Runs on**: Every push & pull request
**Depends on**: Tests must pass

### Stage 3: Deploy to AWS
```
✓ Build SAM application
✓ Deploy to CloudFormation
✓ Create Lambda functions
✓ Setup API Gateway
✓ Create DynamoDB tables (if needed)
```
**Runs on**: Only when push to `main` branch
**Depends on**: Frontend build must succeed

---

## 📊 Architecture

```
Push to main
    ↓
GitHub Actions Triggered
    ├─→ Test Backend
    │   └─→ On Success
    ├─→ Build Frontend  
    │   └─→ On Test Pass
    └─→ Deploy to AWS
        └─→ On Build Success
            ├─→ SAM Build
            ├─→ CloudFormation Deploy
            └─→ Get API Endpoint
```

---

## 🛠️ Manual Deployment (If Pipeline Fails)

### Option 1: Docker-based
```bash
cd C:\Users\KASUN\GIT\ExamBuddy

# Build image
docker build -f Dockerfile.deploy -t exambuddy-deploy:latest .

# Run build
docker run -it -v $(pwd):/app -w /app/backend exambuddy-deploy:latest sam build

# Run deploy
docker run -it \
  -v $(pwd):/app \
  -v $HOME/.aws:/root/.aws \
  -w /app/backend \
  exambuddy-deploy:latest \
  sam deploy --guided
```

### Option 2: Local (requires Python 3.11)
```bash
cd backend

# Build
sam build

# Deploy
sam deploy --guided
```

---

## 🔧 Troubleshooting

### ❌ "Authentication failed"
- Check GitHub Secrets are correctly set
- Verify AWS credentials are valid: `aws sts get-caller-identity`

### ❌ "User is not authorized to perform: iam:CreateRole"
- **CRITICAL**: Admin must grant IAM permissions or pre-create the role
- See [CICD_PIPELINE_SETUP.md](./CICD_PIPELINE_SETUP.md) for admin tasks

### ❌ "S3 bucket does not exist"
- Create buckets before deployment (see Step 2)
- Or let SAM auto-create with `--guided` mode

### ❌ "Build timeout or stuck"
- GitHub Actions jobs timeout after 6 hours
- Check logs for stuck steps
- Restart workflow manually

### ✓ How to view detailed logs
1. Go to GitHub → **Actions** tab
2. Click the failed workflow run
3. Click the failed job
4. Expand "Run SAM deploy" or other step
5. Review the error message

---

## 📈 Next Steps

### Immediate
- [ ] Add GitHub Secrets
- [ ] Create AWS resources (S3, DynamoDB)
- [ ] Commit workflow files
- [ ] Test first deployment

### Short-term
- [ ] Setup CloudWatch alarms
- [ ] Add API monitoring
- [ ] Create frontend deployment step
- [ ] Setup email notifications

### Long-term
- [ ] Production environment
- [ ] Staging environment with separate stack
- [ ] Blue-green deployments
- [ ] Database migrations in pipeline
- [ ] Cost monitoring

---

## 📞 Need Help?

### For AWS Permission Issues (Contact Admin)
Admin needs to:
1. Create `ExamBuddyCIPipelineRole` with Admin access
2. Grant `iam:PassRole`, `iam:CreateRole` permissions
3. Setup GitHub OIDC provider (optional for better security)

### For GitHub Actions Issues
- Check workflow syntax: `.github/workflows/deploy.yml`
- View logs in GitHub → Actions
- Test locally with `act` tool

### For SAM/Lambda Issues
- View CloudFormation events:
  ```bash
  aws cloudformation describe-stack-events --stack-name exambuddy-staging
  ```
- Check Lambda logs:
  ```bash
  aws logs tail /aws/lambda/ExamBuddyFunction --follow
  ```

---

## 🎯 Files Added

```
.
├── .github/
│   └── workflows/
│       └── deploy.yml                 ← GitHub Actions workflow
├── backend/
│   └── samconfig.toml                 ← SAM configuration
├── CICD_PIPELINE_SETUP.md            ← Detailed setup guide
└── CICD_PIPELINE_QUICKSTART.md       ← This file
```

---

## ✅ Checklist Before First Deployment

- [ ] GitHub Secrets configured
- [ ] AWS S3 buckets created
- [ ] DynamoDB table exists
- [ ] IAM user has proper permissions
- [ ] Workflow file in `.github/workflows/`
- [ ] SAM template is valid
- [ ] Docker image builds locally (optional)

---

**Last Updated**: February 17, 2026  
**Status**: Ready for Deployment ✅

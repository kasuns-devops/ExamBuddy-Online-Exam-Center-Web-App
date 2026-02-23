# 🚀 AWS Deployment Instructions

**Status**: Ready for deployment  
**Branch**: main (merged and pushed to GitHub)  
**Date**: February 17, 2026

---

## ⚠️ Important Note: Python Version

**Current Issue**: Your system has Python 3.14, but AWS SAM CLI requires Python 3.9-3.13.

### **Solution Options:**

#### **Option A: Use Python 3.13 (Recommended - Fast)**
1. Install Python 3.13 from python.org
2. Create new venv with Python 3.13:
   ```bash
   py -3.13 -m venv .venv-py313
   .venv-py313\Scripts\activate
   pip install -r backend/requirements.txt
   pip install aws-sam-cli
   ```
3. Then proceed with deployment steps below

#### **Option B: Use Docker (If Installed)**
```bash
docker run -it -v $(pwd):/app python:3.13-slim bash
cd /app/backend
pip install aws-sam-cli
sam build
sam deploy --guided
```

#### **Option C: Use AWS Console (Manual)**
1. Upload code to GitHub (✅ Already done)
2. Use AWS CodePipeline to deploy directly from GitHub
3. Create CloudFormation stack manually

---

## 📋 Deployment Steps (Once Python 3.13 is available)

### **Step 1: Prepare Environment**
```bash
# Activate Python 3.13 environment
.venv-py313\Scripts\activate

# Navigate to backend
cd backend
```

### **Step 2: Build SAM Application**
```bash
sam build
```

**What this does:**
- Downloads dependencies
- Creates `.aws-sam/build` directory
- Packages Python code with CloudFormation template

**Expected output:**
```
Build Succeeded

Built Artifacts  : .aws-sam/build
Built Template   : .aws-sam/build/template.yaml
```

### **Step 3: Deploy to AWS (Guided)**
```bash
sam deploy --guided
```

**You'll be prompted for:**

1. **Stack Name**: Enter (example: `exambuddy-staging`)
2. **AWS Region**: Choose (example: `us-east-1`)
3. **Confirm parameters:**
   - `DynamoDBTableName`: exambuddy-main (or your choice)
   - `S3PdfsBucket`: exambuddy-pdfs-staging (must be globally unique!)
   - `S3ExportsBucket`: exambuddy-exports-staging (must be globally unique!)
   - `CognitoUserPoolId`: (leave empty for now, can update manually)
   - `CognitoClientId`: (leave empty for now, can update manually)
   - `JWTSecret`: (generate a secure secret, example: `your-secret-key-here-min-32-chars`)

4. **S3 Bucket for SAM**: SAM will create an S3 bucket for artifacts
5. **Capabilities**: Confirm `CAPABILITY_IAM` and `CAPABILITY_NAMED_IAM`

**Expected output:**
```
Successfully created/updated stack - exambuddy-staging in [region]
CloudFormation outputs:
  ExamBuddyApiUrl: https://[random].execute-api.[region].amazonaws.com/prod/
```

### **Step 4: Copy Important Information**

Once deployment completes, save these from CloudFormation outputs:
- API Gateway URL
- DynamoDB Table Name
- S3 Bucket ARNs

Example to retrieve:
```bash
aws cloudformation describe-stacks --stack-name exambuddy-staging \
  --query 'Stacks[0].Outputs' --region us-east-1
```

### **Step 5: Configure Frontend**

Update frontend API endpoint in `.env` or `config`:
```bash
VITE_API_URL=https://[your-api-gateway-url]/prod
```

Then rebuild frontend:
```bash
cd frontend
npm run build
```

### **Step 6: Update Cognito (Manual Step)**

After SAM deployment, you'll need to set up Cognito manually or via AWS Console:
1. Create User Pool in AWS Cognito
2. Create App Client
3. Update template parameters with IDs
4. Redeploy:
   ```bash
   sam deploy --parameter-overrides \
     CognitoUserPoolId=your-pool-id \
     CognitoClientId=your-client-id \
     JWTSecret=your-secret
   ```

---

## 🔄 Deployment Flow Summary

```
Python 3.13 Setup
    ↓
SAM Build (.aws-sam/build created)
    ↓
SAM Deploy --guided (AWS resources created)
    ↓
CloudFormation Stack (exambuddy-staging)
    ↓
Lambda Functions, DynamoDB, S3, API Gateway
    ↓
Staging Endpoints Live
    ↓
Test with Real AWS Services
    ↓
Production Deployment (same process, new stack)
```

---

## 📊 Estimated Timeline

| Task | Duration |
|------|----------|
| Python 3.13 Install | 5 minutes |
| SAM Build | 2 minutes |
| SAM Deploy (guided) | 15 minutes |
| AWS Resource Creation | 5 minutes |
| Manual Cognito Setup | 10 minutes |
| Frontend Rebuild | 2 minutes |
| **Total** | **~40 minutes** |

---

## 🧪 Testing After Deployment

### **1. Verify API is Live**
```bash
curl https://[your-api-gateway-url]/prod/health
```

### **2. Test PDF Upload Endpoint**
```bash
curl -X POST \
  https://[your-api-gateway-url]/prod/api/questions/upload-pdf \
  -F "file=@sample_questions.pdf"
```

### **3. Check CloudWatch Logs**
```bash
aws logs tail /aws/lambda/exambuddy-functions --follow
```

### **4. Check DynamoDB Tables**
```bash
aws dynamodb scan --table-name exambuddy-main --region us-east-1
```

---

## 🛠️ Troubleshooting

### **Error: "S3 bucket already exists"**
**Solution**: S3 bucket names must be globally unique. Use a unique prefix:
```bash
exambuddy-pdfs-staging-[your-name-here]
```

### **Error: "Cognito User Pool ID not found"**
**Solution**: 
1. Create Cognito User Pool first
2. Note the Pool ID
3. Pass as parameter during deployment

### **Error: "Lambda execution role not found"**
**Solution**: Ensure AWS credentials are configured:
```bash
aws configure
```

### **Error: "Insufficient permissions"**
**Solution**: Verify IAM user has these permissions:
- CloudFormation
- Lambda
- DynamoDB
- S3
- API Gateway
- Cognito
- IAM (for creating roles)

---

## 📝 Next Steps After Staging Deployment

1. ✅ Test all endpoints with real AWS services
2. ✅ Verify PDF upload works
3. ✅ Check question type detection
4. ✅ Test authentication flow
5. 🎯 **Then**: Deploy to production with same steps

---

## 🔑 Key AWS CLI Commands Reference

```bash
# View stack status
aws cloudformation describe-stacks --stack-name exambuddy-staging

# View stack events
aws cloudformation describe-stack-events --stack-name exambuddy-staging

# View Lambda logs
aws logs tail /aws/lambda/exambuddy-functions --follow

# Invoke Lambda directly
aws lambda invoke --function-name exambuddy-health-function output.json

# List DynamoDB tables
aws dynamodb list-tables

# Scan DynamoDB table
aws dynamodb scan --table-name exambuddy-main

# Delete stack (cleanup)
aws cloudformation delete-stack --stack-name exambuddy-staging
```

---

## ✅ Deployment Readiness Checklist

- [x] Code merged to main branch
- [x] Code pushed to GitHub
- [x] Backend code ready
- [x] Frontend code ready
- [x] template.yaml configured
- [x] All tests passing
- [x] AWS CLI installed
- [ ] Python 3.13 installed (DO THIS FIRST)
- [ ] AWS credentials configured
- [ ] SAM CLI installed (will work with Python 3.13)
- [ ] S3 bucket names decided (must be unique globally)
- [ ] AWS region chosen (recommend: us-east-1)
- [ ] Cognito setup plan ready

---

## 🚀 Ready to Deploy?

**Next Action:**
1. Install Python 3.13
2. Create new venv with Python 3.13
3. Run: `sam build`
4. Run: `sam deploy --guided`

**Questions?** Refer to [NEXT_STEPS.md](NEXT_STEPS.md) for additional context.

---

**Deployment Status**: ✅ Ready  
**Blocker**: Python 3.14 not supported by SAM (use Python 3.13)  
**Solution**: Use Python 3.13 venv or Docker

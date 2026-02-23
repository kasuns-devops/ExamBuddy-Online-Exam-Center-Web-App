# 🐳 Docker Deployment - Quick Start (Option 2)

## ✅ Setup Complete

I've created everything you need for Docker deployment:

### **Files Created:**
1. ✅ `Dockerfile.deploy` - Docker image for SAM deployment
2. ✅ `deploy.bat` - Windows batch deployment script
3. ✅ `deploy.ps1` - PowerShell deployment script
4. ✅ `DOCKER_DEPLOYMENT_GUIDE.md` - Complete guide

---

## 🚀 Quick Start (5 Minutes)

### **Step 1: Start Docker Desktop**
- Open Start Menu
- Search for "Docker Desktop"
- Click to start
- Wait for the Docker icon in system tray (1-2 minutes)

### **Step 2: Open PowerShell**
```powershell
cd C:\Users\KASUN\GIT\ExamBuddy
```

### **Step 3: Configure AWS Credentials**
```powershell
aws configure
```

You'll be prompted for:
- **Access Key ID**: Your AWS access key
- **Secret Access Key**: Your AWS secret key  
- **Default region**: `us-east-1`
- **Output format**: `json`

### **Step 4: Run Deployment Script**

**Option A - PowerShell (Recommended):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\deploy.ps1
```

**Option B - Command Prompt (Windows):**
```cmd
deploy.bat
```

### **Step 5: Answer Deployment Questions**

When prompted, provide:

| Prompt | Answer | Example |
|--------|--------|---------|
| Stack Name | `exambuddy-staging` | `exambuddy-staging` |
| AWS Region | `us-east-1` | `us-east-1` |
| DynamoDBTableName | `exambuddy-main` | `exambuddy-main` |
| S3PdfsBucket | **UNIQUE NAME** | `exambuddy-pdfs-kasun-2026` |
| S3ExportsBucket | **UNIQUE NAME** | `exambuddy-exports-kasun-2026` |
| CognitoUserPoolId | Leave blank | (press Enter) |
| CognitoClientId | Leave blank | (press Enter) |
| JWTSecret | Secure secret | `SecureKey123!@#MinLength32Chars` |
| Samconfig.toml | Confirm | `Y` |
| Capabilities | Confirm | `Y` |

---

## 📊 What Happens Automatically

```
Your computer                          Docker Container
┌─────────────────┐                  ┌──────────────────┐
│ Run deploy.ps1  │  ──────────────▶ │ Python 3.13      │
│ (or deploy.bat) │                  │ AWS SAM CLI       │
└─────────────────┘                  │ AWS CLI          │
                                     │ boto3            │
                                     └──────────────────┘
                                            │
                                            ▼
                                     ┌──────────────────┐
                                     │ sam build        │
                                     │ sam deploy       │
                                     └──────────────────┘
                                            │
                                            ▼
                                     ┌──────────────────┐
                                     │ AWS CloudFormation
                                     │ Creates:         │
                                     │ - Lambda Func   │
                                     │ - API Gateway   │
                                     │ - DynamoDB      │
                                     │ - S3 Buckets    │
                                     └──────────────────┘
```

---

## ⏱️ Timeline

| Step | Duration |
|------|----------|
| Start Docker | 2 min |
| Configure AWS | 1 min |
| Script runs (auto) | 25 min |
| **Total** | **~30 min** |

---

## 📝 Important Notes

### **S3 Bucket Names MUST be Unique**
S3 bucket names are globally unique across all AWS accounts. If you see:
```
Error: S3 bucket 'exambuddy-pdfs' already exists
```

Change the name to something unique:
```
exambuddy-pdfs-kasun-2026
exambuddy-exports-kasun-2026
```

### **AWS Credentials**
- Credentials go in: `%USERPROFILE%/.aws/credentials`
- Config goes in: `%USERPROFILE%/.aws/config`
- The script automatically mounts these into Docker

### **What Docker Does**
- ✅ Creates isolated Python 3.13 environment
- ✅ Installs AWS SAM CLI (which doesn't work with Python 3.14)
- ✅ Builds your CloudFormation template
- ✅ Deploys to AWS
- ✅ Your local files are NOT modified

---

## 🎯 After Deployment Completes

The script will output something like:

```
CloudFormation outputs:
  ExamBuddyApiUrl: https://abcd1234.execute-api.us-east-1.amazonaws.com/prod/
  DynamoDBTableName: exambuddy-main
  S3PdfsBucket: exambuddy-pdfs-kasun-2026
```

**Save these values!** You'll need them for:
1. Frontend API configuration
2. Testing endpoints
3. Production deployment

---

## ✅ Checklist Before Running

- [ ] Docker Desktop installed (✓ You have it)
- [ ] Docker Desktop started
- [ ] AWS credentials configured (`aws configure`)
- [ ] AWS account has sufficient permissions
- [ ] S3 bucket names decided (must be unique)
- [ ] Ready to run script

---

## 🛠️ If Something Goes Wrong

### **Error: Docker not found**
```powershell
# Make sure Docker Desktop is running
docker ps
```

### **Error: AWS credentials not found**
```powershell
aws configure
# Then re-run script
```

### **Error: S3 bucket already exists**
**Solution**: Use a unique name:
```
exambuddy-pdfs-yourname-date
```

### **Error: Permission denied**
**Solution**: Run PowerShell as Administrator

### **Error: SAM deployment failed**
**Solution**: Check CloudWatch logs:
```bash
docker run -it -v %USERPROFILE%/.aws:/root/.aws -v C:/Users/KASUN/GIT/ExamBuddy:/app python:3.13-slim bash
# Inside container:
aws logs tail /aws/lambda --follow
```

---

## 📞 Support

For detailed information, see:
- `DOCKER_DEPLOYMENT_GUIDE.md` - Complete guide
- `AWS_DEPLOYMENT_INSTRUCTIONS.md` - AWS-specific info
- `NEXT_STEPS.md` - After deployment

---

## 🚀 Ready?

### **DO THIS NOW:**

1. ✅ Start Docker Desktop (wait 2 minutes)
2. ✅ Run: `aws configure`
3. ✅ Run: `.\deploy.ps1` (or `deploy.bat`)
4. ✅ Answer the prompts
5. ✅ Wait for deployment to complete

### **Result:** 
Your staging environment will be live on AWS! 🎉

---

**Status**: ✅ Ready for deployment  
**Method**: Docker + SAM CLI  
**Time**: ~30 minutes  
**Complexity**: Low (script handles everything)

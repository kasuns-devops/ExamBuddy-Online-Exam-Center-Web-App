# Option 2: Docker Deployment - Step-by-Step

## 4️⃣ SIMPLE STEPS

```
STEP 1                 STEP 2                 STEP 3                 STEP 4
┌─────────────┐       ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│ Start Docker│       │ Configure   │       │   Run Script│       │    Enjoy    │
│   Desktop   │  ──▶  │     AWS     │  ──▶  │ (automated) │  ──▶  │    Live     │
│             │       │  Creds      │       │             │       │    AWS      │
└─────────────┘       └─────────────┘       └─────────────┘       └─────────────┘
    2 min                 1 min                  25 min              ✅ Done
```

---

## 📋 EXECUTION CHECKLIST

### **Before Starting:**
```
☐ Docker Desktop is installed (YOU HAVE IT ✓)
☐ Docker Desktop is running
☐ AWS account is ready
☐ AWS credentials available
☐ In correct directory: C:\Users\KASUN\GIT\ExamBuddy
```

---

## 🚀 EXACT COMMANDS TO RUN

### **1. Start Docker Desktop (2 min)**
```
Click: Start Menu → Docker Desktop → Wait for icon in system tray
Verify: docker ps (should show CONTAINER ID header)
```

### **2. Open PowerShell (1 min)**
```powershell
# Right-click Start Menu
# Choose "Windows PowerShell (Admin)" or "Terminal (Admin)"

# Navigate to project
cd C:\Users\KASUN\GIT\ExamBuddy

# Check we're in right place
ls  # Should show: backend, frontend, deploy.ps1, etc.
```

### **3. Configure AWS Credentials (1 min)**
```powershell
aws configure
```

**When prompted, enter:**
```
AWS Access Key ID: [Your AWS Access Key]
AWS Secret Access Key: [Your AWS Secret Key]
Default region name: us-east-1
Default output format: json
```

**To get these:**
- Go to AWS Console → IAM → Users → Your User → Security Credentials
- Click "Create access key" if needed

### **4. Run Deployment Script (25 min)**
```powershell
# Allow script execution (one-time)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run the script
.\deploy.ps1
```

---

## 📝 WHAT TO ANSWER WHEN PROMPTED

```
Script asks:                          You answer:
─────────────────────────────────────────────────────────────

Stack Name                      → exambuddy-staging

AWS Region                      → us-east-1

DynamoDBTableName              → exambuddy-main

S3PdfsBucket                   → exambuddy-pdfs-[yourname]-2026
                                  (MUST BE UNIQUE!)

S3ExportsBucket                → exambuddy-exports-[yourname]-2026
                                  (MUST BE UNIQUE!)

CognitoUserPoolId              → [leave blank, just press Enter]

CognitoClientId                → [leave blank, just press Enter]

JWTSecret                      → YourSecureKey123!@#ValidMin32Chars

Save samconfig.toml?           → Y

Confirm capabilities?          → Y
```

---

## ✅ SUCCESS INDICATORS

### **Build Phase Success:**
```
✓ Building container image
✓ Installing Python 3.13
✓ Installing AWS SAM CLI
✓ SAM build starts
✓ .aws-sam/build directory created
```

### **Deploy Phase Success:**
```
✓ SAM deploy starts
✓ CloudFormation stack creation begins
✓ Resources being created...
✓ Resources created successfully
✓ Stack outputs displayed
```

### **Final Output (SAVE THESE!):**
```
CloudFormation outputs:
  ExamBuddyApiUrl: https://xxxxx.execute-api.us-east-1.amazonaws.com/prod/
  DynamoDBTableName: exambuddy-main
  S3PdfsBucket: exambuddy-pdfs-[yourname]-2026
```

---

## 🎯 AFTER DEPLOYMENT

### **1. Save the API URL**
```
Example: https://abcd1234.execute-api.us-east-1.amazonaws.com/prod/

You'll need this for:
- Frontend configuration
- Testing endpoints
- Production deployment
```

### **2. Test the Deployment**
```powershell
# Replace with your actual URL
$API_URL = "https://abcd1234.execute-api.us-east-1.amazonaws.com/prod"

# Test health endpoint
curl.exe -X GET "$API_URL/health"

# Should return: {"status": "healthy", "version": "1.0.0"}
```

### **3. Next: Update Frontend**
```
Frontend API config file: frontend/src/services/api.js
Update with your API_URL from above
```

---

## ⚠️ COMMON ISSUES & FIXES

### **Issue: "Docker is not running"**
```
Fix: Start Docker Desktop from Start Menu and wait 2 minutes
Verify: Run 'docker ps' - should show CONTAINER ID header
```

### **Issue: "AWS credentials not configured"**
```
Fix: Run 'aws configure' and enter your AWS access keys
Location: %USERPROFILE%\.aws\credentials
```

### **Issue: "S3 bucket already exists"**
```
Fix: S3 names must be globally unique
Change: exambuddy-pdfs-[yourname]-[date]
Example: exambuddy-pdfs-kasun-20260217
```

### **Issue: "Permission denied" or "Access Denied"**
```
Fix: Run PowerShell as Administrator
Right-click PowerShell → Run as Administrator
Or use: Windows Terminal (Admin)
```

### **Issue: Script stops/hangs**
```
Fix: Press Ctrl+C and re-run
Cause: Usually timeout or network issue
Solution: Check internet and AWS credentials
```

---

## 📊 WHAT'S HAPPENING IN DOCKER

```
Your Computer          Docker Container (Python 3.13)
────────────────────   ────────────────────────────────
deploy.ps1
   │
   ├─ Build image ────▶ Dockerfile.deploy
   │                    - Python 3.13
   │                    - AWS CLI
   │                    - SAM CLI
   │
   ├─ Mount volumes ──▶ /app (your code)
   │                    /root/.aws (credentials)
   │
   ├─ Run sam build ──▶ Reads template.yaml
   │                    Compiles code
   │                    Creates .aws-sam/build/
   │
   └─ Run sam deploy ─▶ Reads template
      (guided)          Asks you questions
                        Calls AWS CloudFormation
                        Creates resources
                        Returns outputs
```

---

## 🎁 FILES CREATED FOR YOU

```
✅ Dockerfile.deploy          - Docker image definition
✅ deploy.ps1                 - PowerShell deployment script
✅ deploy.bat                 - Batch deployment script
✅ DOCKER_QUICK_START.md      - This guide
✅ DOCKER_DEPLOYMENT_GUIDE.md - Detailed reference
✅ AWS_DEPLOYMENT_INSTRUCTIONS.md - AWS reference
```

---

## 🚀 READY TO GO?

### **Your Next 3 Actions:**

```
1️⃣  Start Docker Desktop
    └─ Wait for system tray icon (2 min)

2️⃣  Run: aws configure
    └─ Enter your AWS access keys (1 min)

3️⃣  Run: .\deploy.ps1
    └─ Answer the prompts (25 min total)
    └─ Wait for "✓ Deployment Complete" message
```

### **Expected Total Time: ~30 minutes**

---

## 📞 NEED HELP?

If something goes wrong:

1. **Read the error message** - usually tells you what's wrong
2. **Check Docker is running** - `docker ps`
3. **Check AWS credentials** - `aws sts get-caller-identity`
4. **See troubleshooting** - See section above
5. **Check guides** - DOCKER_DEPLOYMENT_GUIDE.md

---

## ✨ THAT'S IT!

You now have everything needed for Docker deployment.

**Start with:**
```powershell
.\deploy.ps1
```

Let me know when Docker is running and you're ready to execute! 🚀

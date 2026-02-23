# 🐳 Docker Deployment Guide - Option 2

## Prerequisites Check

Your system has Docker installed ✅ (`Docker version 29.1.3`)

**However**: Docker daemon is not currently running.

---

## 📋 Steps to Proceed with Docker Option 2

### **Step 1: Start Docker Desktop**

1. Open **Docker Desktop** from your Start Menu
2. Wait for it to fully start (icon appears in system tray)
3. Verify it's running:
   ```powershell
   docker ps
   ```
   Should show: `CONTAINER ID   IMAGE   COMMAND   CREATED   STATUS   PORTS   NAMES`

---

### **Step 2: Build Docker Container for Deployment**

Create a Dockerfile for SAM deployment:

```dockerfile
# Dockerfile.deploy
FROM python:3.13-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install AWS SAM CLI
RUN pip install --no-cache-dir aws-sam-cli

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app/

# Verify SAM installation
RUN sam --version

CMD ["/bin/bash"]
```

**To use this:**
1. Save as `Dockerfile.deploy` in project root
2. Build:
   ```bash
   docker build -f Dockerfile.deploy -t exambuddy-deploy:latest .
   ```

---

### **Step 3: Run SAM Build in Docker**

Once Docker is running and image is built:

```bash
docker run -it \
  -v C:/Users/KASUN/GIT/ExamBuddy:/app \
  -w /app/backend \
  exambuddy-deploy:latest \
  sam build
```

**What this does:**
- `-it`: Interactive terminal
- `-v`: Mount local folder into container
- `-w`: Working directory in container
- `sam build`: Builds your application

**Expected output:**
```
Build Succeeded

Built Artifacts  : .aws-sam/build
Built Template   : .aws-sam/build/template.yaml
```

---

### **Step 4: Run SAM Deploy in Docker (Guided)**

```bash
docker run -it \
  -v C:/Users/KASUN/GIT/ExamBuddy:/app \
  -v %USERPROFILE%/.aws:/root/.aws \
  -w /app/backend \
  exambuddy-deploy:latest \
  sam deploy --guided
```

**Important**: 
- `-v %USERPROFILE%/.aws:/root/.aws` mounts your AWS credentials
- Make sure your AWS credentials are configured locally first:
  ```bash
  aws configure
  ```

**You'll be prompted for:**
- Stack name: `exambuddy-staging`
- AWS Region: `us-east-1`
- Parameters (see below)
- Confirm deployments

---

### **Step 5: Configure AWS Credentials (Required)**

Before Docker deployment, configure AWS credentials:

```bash
aws configure
```

You'll be prompted for:
1. AWS Access Key ID
2. AWS Secret Access Key
3. Default region: `us-east-1`
4. Output format: `json`

These get saved to: `%USERPROFILE%/.aws/`

---

### **Step 6: Parameter Configuration for SAM Deploy**

When you run `sam deploy --guided`, you'll be asked for:

| Parameter | Value | Example |
|-----------|-------|---------|
| Stack Name | Your choice | `exambuddy-staging` |
| AWS Region | Preferred region | `us-east-1` |
| DynamoDBTableName | Table name | `exambuddy-main` |
| S3PdfsBucket | **MUST BE UNIQUE** | `exambuddy-pdfs-kasun-2026` |
| S3ExportsBucket | **MUST BE UNIQUE** | `exambuddy-exports-kasun-2026` |
| CognitoUserPoolId | Leave blank | (set up later) |
| CognitoClientId | Leave blank | (set up later) |
| JWTSecret | Secure string | `your-secret-key-32-chars-min` |
| Confirm changes | Yes | `y` |
| Capabilities | Confirm | `y` |

---

## 🔑 Quick Docker Commands Reference

### **List containers:**
```bash
docker ps -a
```

### **Remove container:**
```bash
docker rm [container-id]
```

### **Remove image:**
```bash
docker rmi exambuddy-deploy:latest
```

### **View Docker logs:**
```bash
docker logs [container-id]
```

### **Execute command in running container:**
```bash
docker exec -it [container-id] bash
```

---

## 📊 Complete Docker Workflow

```
1. Start Docker Desktop
   ↓
2. Configure AWS credentials (aws configure)
   ↓
3. Create Dockerfile.deploy
   ↓
4. Build Docker image (docker build -f Dockerfile.deploy -t exambuddy-deploy:latest .)
   ↓
5. Run SAM build in container (docker run ... sam build)
   ↓
6. Run SAM deploy in container (docker run ... sam deploy --guided)
   ↓
7. Answer prompted questions
   ↓
8. CloudFormation creates resources
   ↓
9. Deployment complete ✅
```

---

## ⏱️ Estimated Timeline

| Step | Duration |
|------|----------|
| Start Docker Desktop | 2 minutes |
| Configure AWS credentials | 2 minutes |
| Create Dockerfile.deploy | 1 minute |
| Build Docker image | 3 minutes |
| SAM build in container | 2 minutes |
| SAM deploy (interactive) | 15-20 minutes |
| **Total** | **~30 minutes** |

---

## ✅ Pre-Deployment Checklist

- [ ] Docker Desktop started and running
- [ ] AWS credentials configured (`aws configure`)
- [ ] S3 bucket names decided (must be globally unique!)
- [ ] AWS region chosen (recommend: `us-east-1`)
- [ ] Dockerfile.deploy created
- [ ] Docker image built successfully
- [ ] Ready to deploy

---

## 🚨 Troubleshooting

### **Docker daemon not running**
**Solution**: Start Docker Desktop from Start Menu and wait 30-60 seconds for it to fully start

### **Error: "permission denied"**
**Solution**: Run PowerShell as Administrator

### **Error: "connection refused" in container**
**Solution**: Ensure AWS credentials are properly configured:
```bash
aws sts get-caller-identity
```

### **Error: "S3 bucket already exists"**
**Solution**: S3 names must be globally unique. Use:
```
exambuddy-pdfs-yourname-date
exambuddy-exports-yourname-date
```

### **Error: "no such file or directory"**
**Solution**: Ensure volume mount path is correct:
```bash
# Windows path format with forward slashes
docker run -v C:/Users/KASUN/GIT/ExamBuddy:/app ...
```

---

## 📝 Next Steps

### **Immediate (Do Now):**
1. ✅ Start Docker Desktop
2. ✅ Run: `aws configure`
3. ✅ Create Dockerfile.deploy (save code below)
4. ✅ Build image: `docker build -f Dockerfile.deploy -t exambuddy-deploy:latest .`
5. ✅ Run SAM build
6. ✅ Run SAM deploy

### **After Deployment:**
1. Note API Gateway URL
2. Update frontend with API URL
3. Test endpoints
4. Deploy to production

---

## 🔧 Ready-to-Use Dockerfile

Save this as `Dockerfile.deploy` in project root:

```dockerfile
FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install AWS CLI and SAM CLI
RUN pip install --no-cache-dir \
    awscli \
    aws-sam-cli \
    boto3

# Verify installations
RUN aws --version && sam --version

# Set working directory
WORKDIR /app

# Default command
CMD ["/bin/bash"]
```

---

## 🎯 Ready to Start?

**Next action:**
1. Start Docker Desktop
2. Wait for it to be fully running (check system tray)
3. Configure AWS credentials: `aws configure`
4. Come back and tell me when Docker is ready!

---

**Setup Guide**: Complete  
**Status**: Ready for Docker deployment  
**Blocker**: Docker daemon needs to be running

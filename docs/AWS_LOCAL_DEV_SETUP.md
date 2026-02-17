# AWS Local Development Setup

## Create IAM User for Local Development

### Step 1: Create IAM User in AWS Console

1. Go to AWS Console → IAM → Users → Create user
2. User name: `exambuddy-local-dev` (or your preferred name)
3. ✅ Enable "Provide user access to the AWS Management Console" (optional)
4. Click "Next"

### Step 2: Attach Permissions

Attach the same policies as github-actions-deployer:
- AmazonCognitoPowerUser
- AmazonDynamoDBFullAccess
- AmazonS3FullAccess
- CloudFormationFullAccess
- IAMReadOnlyAccess

Or create inline policy with minimal permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cognito-idp:*",
                "dynamodb:*",
                "s3:*"
            ],
            "Resource": "*"
        }
    ]
}
```

### Step 3: Create Access Keys

1. Go to IAM → Users → [your-user] → Security credentials
2. Click "Create access key"
3. Select "Command Line Interface (CLI)"
4. ✅ Acknowledge recommendation
5. Click "Create access key"
6. **Important**: Save both keys:
   - Access key ID: `AKIA...`
   - Secret access key: `wJalr...` (only shown once!)

### Step 4: Configure AWS CLI

Run in terminal:
```bash
aws configure
```

Enter when prompted:
```
AWS Access Key ID: [paste your access key ID]
AWS Secret Access Key: [paste your secret access key]
Default region name: eu-north-1
Default output format: json
```

### Step 5: Verify Configuration

```bash
# Check configuration
aws configure list

# Test connection
aws sts get-caller-identity

# Test Cognito
aws cognito-idp describe-user-pool --user-pool-id eu-north-1_SoMYr0sug --region eu-north-1

# Test DynamoDB
aws dynamodb describe-table --table-name exambuddy-main-dev --region eu-north-1

# Test S3
aws s3 ls s3://exambuddy-pdfs-dev-887863153274/
```

### Step 6: Run ExamBuddy AWS Connectivity Test

```bash
cd backend
python test_aws_connectivity.py
```

Expected output:
```
✅ Cognito User Pool: exambuddy-resources-dev-UserPool
✅ DynamoDB Table: exambuddy-main-dev
✅ S3 Bucket: exambuddy-pdfs-dev-887863153274
✅ S3 Bucket: exambuddy-exports-dev-887863153274
🎉 All AWS services are accessible!
```

## Option B: Use AWS SSO (If your organization uses it)

```bash
aws configure sso
# Follow the prompts to set up SSO
```

## Security Best Practices

1. ✅ **Never commit AWS credentials to git** (already in .gitignore)
2. ✅ **Use separate IAM users** for local dev vs CI/CD
3. ✅ **Rotate access keys regularly** (every 90 days)
4. ✅ **Enable MFA** on your IAM user for extra security
5. ✅ **Use least privilege** - only grant needed permissions

## Credentials Location

AWS CLI stores credentials in:
- **Windows**: `C:\Users\KASUN\.aws\credentials`
- **Config**: `C:\Users\KASUN\.aws\config`

These files are automatically excluded from git (in user directory, not project).

## Troubleshooting

### "Unable to locate credentials"
- Run `aws configure` and enter your credentials
- Verify: `aws configure list`

### "Access Denied" errors
- Check IAM user has required permissions
- Verify correct region: `eu-north-1`

### Region mismatch
- Your resources are in `eu-north-1` (Stockholm)
- Update config: `aws configure set region eu-north-1`

---
**Next Steps**: After AWS CLI is configured, run `python backend/test_aws_connectivity.py` to verify all services are accessible.

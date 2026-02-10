# GitHub Actions Setup Guide

This guide walks you through setting up automated AWS infrastructure deployment using GitHub Actions.

## Prerequisites

- AWS Account with appropriate permissions
- GitHub repository
- AWS CLI installed locally (for cleanup)

## Step 1: Delete Existing Manual Resources

Before automating, clean up manually created resources to avoid conflicts.

### Option A: Using the Cleanup Script (Recommended)

```bash
# Make script executable
chmod +x infrastructure/cleanup-manual-resources.sh

# Run cleanup
./infrastructure/cleanup-manual-resources.sh
```

### Option B: Manual Deletion via AWS Console

1. **Cognito User Pool**:
   - Navigate to AWS Cognito → User Pools
   - Select `exambuddy-users` (or your pool name)
   - Click "Delete" → Confirm

2. **DynamoDB Table**:
   - Navigate to DynamoDB → Tables
   - Select `exambuddy-main`
   - Actions → Delete → Confirm

3. **S3 Buckets**:
   - Navigate to S3
   - For each bucket (`exambuddy-pdfs-*`, `exambuddy-exports-*`):
     - Empty bucket first (select all → Actions → Delete)
     - Delete bucket

### Option C: AWS CLI Commands

```bash
# Delete Cognito User Pool
aws cognito-idp delete-user-pool \
  --user-pool-id eu-north-1_KOieq5GAE \
  --region eu-north-1

# Delete DynamoDB Table
aws dynamodb delete-table \
  --table-name exambuddy-main \
  --region eu-north-1

# Delete S3 Buckets (adjust bucket names as needed)
aws s3 rb s3://exambuddy-pdfs-dev-ACCOUNT_ID --force --region eu-north-1
aws s3 rb s3://exambuddy-exports-dev-ACCOUNT_ID --force --region eu-north-1
```

## Step 2: Create AWS IAM User for GitHub Actions

### Via AWS Console:

1. Navigate to **IAM** → **Users** → **Create user**
2. User name: `github-actions-deployer`
3. Select **"Attach policies directly"**
4. Add these managed policies:
   - `AmazonCognitoPowerUser`
   - `AmazonDynamoDBFullAccess`
   - `AmazonS3FullAccess`
   - `CloudFormationFullAccess`
   - `IAMReadOnlyAccess`
5. Create user
6. Go to **Security credentials** → **Create access key**
7. Select **"Third-party service"** → Check the confirmation → Create
8. **Save the Access Key ID and Secret Access Key** (you won't see them again!)

### Or use this custom policy (more restrictive):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "cognito-idp:*",
        "dynamodb:*",
        "s3:*",
        "iam:GetRole",
        "iam:PassRole"
      ],
      "Resource": "*"
    }
  ]
}
```

## Step 3: Configure GitHub Secrets

1. Navigate to your GitHub repository
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add these secrets:

   | Secret Name | Value |
   |-------------|-------|
   | `AWS_ACCESS_KEY_ID` | Your IAM user's access key ID |
   | `AWS_SECRET_ACCESS_KEY` | Your IAM user's secret access key |

   **⚠️ Security Note**: Never commit these credentials to your repository!

## Step 4: Update CloudFormation Template (if needed)

The template is already configured for `eu-north-1` region. If you want to change:

Edit [infrastructure/cloudformation-resources.yaml](../infrastructure/cloudformation-resources.yaml):

```yaml
Parameters:
  ProjectName:
    Type: String
    Default: exambuddy
  
  Environment:
    Type: String
    Default: dev  # Change to staging or prod as needed
```

## Step 5: Trigger Deployment

### Automatic Trigger (on Push):

```bash
# Commit and push changes
git add .
git commit -m "ci: add GitHub Actions infrastructure deployment"
git push origin setup-aws-infrastructure
```

The workflow will automatically:
1. ✅ Validate CloudFormation template
2. ✅ Deploy infrastructure
3. ✅ Output resource IDs in the Actions summary

### Manual Trigger:

1. Go to **Actions** tab in GitHub
2. Select **"Deploy AWS Infrastructure"** workflow
3. Click **"Run workflow"**
4. Select environment (dev/staging/prod)
5. Click **"Run workflow"**

## Step 6: Monitor Deployment

1. Go to **Actions** tab in GitHub
2. Click on the running workflow
3. Watch the deployment progress
4. Check the **Summary** for resource IDs after completion

Alternatively, check AWS CloudFormation Console:
- Navigate to **CloudFormation** → **Stacks**
- Find `exambuddy-resources-dev`
- Monitor stack events and status

## Step 7: Update .env Files

After successful deployment, copy the resource IDs from the GitHub Actions summary:

### Backend `.env`:

```bash
# Copy from GitHub Actions output
COGNITO_USER_POOL_ID=eu-north-1_XXXXXXXXX
COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxx
COGNITO_REGION=eu-north-1
DYNAMODB_TABLE_NAME=exambuddy-main-dev
S3_PDFS_BUCKET=exambuddy-pdfs-dev-123456789012
S3_EXPORTS_BUCKET=exambuddy-exports-dev-123456789012

# Other environment variables
AWS_REGION=eu-north-1
ENVIRONMENT=dev
LOG_LEVEL=INFO
```

### Frontend `.env`:

```bash
# Copy from GitHub Actions output
VITE_COGNITO_USER_POOL_ID=eu-north-1_XXXXXXXXX
VITE_COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxx
VITE_COGNITO_REGION=eu-north-1

# API endpoint (local development)
VITE_API_URL=http://localhost:8000
```

## Step 8: Verify Deployment

Check that resources were created:

```bash
# List CloudFormation stack resources
aws cloudformation describe-stack-resources \
  --stack-name exambuddy-resources-dev \
  --region eu-north-1

# Verify Cognito User Pool
aws cognito-idp describe-user-pool \
  --user-pool-id <YOUR_USER_POOL_ID> \
  --region eu-north-1

# Verify DynamoDB Table
aws dynamodb describe-table \
  --table-name exambuddy-main-dev \
  --region eu-north-1

# Verify S3 Buckets
aws s3 ls | grep exambuddy
```

## Troubleshooting

### Deployment Failed

1. Check GitHub Actions logs for error details
2. Check CloudFormation stack events in AWS Console
3. Common issues:
   - **Insufficient permissions**: Update IAM user policy
   - **Resource already exists**: Run cleanup script again
   - **S3 bucket name conflict**: Bucket names are globally unique, the template uses account ID suffix

### Stack Update Shows "No Changes"

This is normal if the template hasn't changed. The workflow will skip the update.

### Rollback Triggered

If deployment fails, CloudFormation automatically rolls back. Check the rollback reason in stack events.

## Clean Up (Delete Everything)

To delete all infrastructure:

```bash
# Delete CloudFormation stack (deletes all resources)
aws cloudformation delete-stack \
  --stack-name exambuddy-resources-dev \
  --region eu-north-1

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete \
  --stack-name exambuddy-resources-dev \
  --region eu-north-1
```

Or via AWS Console:
- Navigate to **CloudFormation** → **Stacks**
- Select `exambuddy-resources-dev`
- Click **Delete** → Confirm

## Multi-Environment Setup

To deploy multiple environments (dev/staging/prod):

1. Update `.github/workflows/deploy-infrastructure.yml`:

```yaml
env:
  STACK_NAME: exambuddy-resources-${{ github.event.inputs.environment || 'dev' }}
```

2. Create environment-specific branches or use workflow dispatch with environment selector

3. Each environment will have separate resources:
   - `exambuddy-main-dev`
   - `exambuddy-main-staging`
   - `exambuddy-main-prod`

## Next Steps

- ✅ Infrastructure deployed via GitHub Actions
- 🔄 Update `.env` files with new resource IDs
- 🚀 Deploy backend and frontend applications
- 📝 Set up application deployment pipelines (separate workflows)

## Resources

- [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

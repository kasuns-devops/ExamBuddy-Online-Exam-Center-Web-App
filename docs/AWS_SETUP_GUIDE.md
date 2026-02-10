# AWS Resource Provisioning Guide

This guide covers manual provisioning of AWS resources required for ExamBuddy. Alternatively, use the CloudFormation template in `infrastructure/cloudformation-resources.yaml`.

## T012: Create AWS Cognito User Pool

### AWS Console Steps:

1. Navigate to **AWS Cognito** → **User Pools** → **Create user pool**
2. Configure sign-in options:
   - ✅ Email
   - Password requirements: Minimum 8 characters
3. Configure security:
   - MFA: Optional (can enable later)
   - Password policy: Default
4. Configure sign-up experience:
   - Enable self-registration
   - Required attributes: email
5. Configure message delivery:
   - Email provider: Cognito default (or SES for production)
6. Integrate your app:
   - User pool name: `exambuddy-users`
   - App client name: `exambuddy-web`
   - ✅ Generate client secret: NO (public client)
7. Add custom attribute:
   - Navigate to **User pool** → **Sign-up experience** → **Custom attributes**
   - Add: `custom:role` (String, Mutable)

**Save these values to `.env` files:**
- User Pool ID: `eu-north-1_KOieq5GAE`
- App Client ID: `2k24r8nsjk6al9g9vjpb5fv1ul`
- Region: `europe`

### CLI Alternative:

```bash
aws cognito-idp create-user-pool \
  --pool-name exambuddy-users \
  --policies "PasswordPolicy={MinimumLength=8,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true,RequireSymbols=false}" \
  --schema "Name=email,Required=true,Mutable=true" "Name=role,AttributeDataType=String,Mutable=true" \
  --auto-verified-attributes email \
  --username-attributes email

# Note the UserPoolId from output

aws cognito-idp create-user-pool-client \
  --user-pool-id YOUR_USER_POOL_ID \
  --client-name exambuddy-web \
  --no-generate-secret \
  --explicit-auth-flows ALLOW_USER_PASSWORD_AUTH ALLOW_REFRESH_TOKEN_AUTH
```

---

## T013: Create DynamoDB Table

### AWS Console Steps:

1. Navigate to **DynamoDB** → **Tables** → **Create table**
2. Table settings:
   - Table name: `exambuddy-main`
   - Partition key: `PK` (String)
   - Sort key: `SK` (String)
3. Table settings:
   - Capacity mode: **On-demand** (recommended for variable load)
   - Or **Provisioned**: 5 RCU, 5 WCU (adjust based on load)
4. Create Global Secondary Indexes (GSIs):

   **GSI-1: GSI1**
   - Partition key: `GSI1PK` (String)
   - Sort key: `GSI1SK` (String)
   - Projected attributes: All

   **GSI-2: GSI2**
   - Partition key: `GSI2PK` (String)
   - Sort key: `GSI2SK` (String)
   - Projected attributes: All

   **GSI-3: GSI3**
   - Partition key: `GSI3PK` (String)
   - Sort key: `GSI3SK` (String)
   - Projected attributes: All

5. Enable:
   - ✅ Point-in-time recovery (PITR)
   - Encryption: AWS owned key

### CLI Alternative:

```bash
aws dynamodb create-table \
  --table-name exambuddy-main \
  --attribute-definitions \
    AttributeName=PK,AttributeType=S \
    AttributeName=SK,AttributeType=S \
    AttributeName=GSI1PK,AttributeType=S \
    AttributeName=GSI1SK,AttributeType=S \
    AttributeName=GSI2PK,AttributeType=S \
    AttributeName=GSI2SK,AttributeType=S \
    AttributeName=GSI3PK,AttributeType=S \
    AttributeName=GSI3SK,AttributeType=S \
  --key-schema \
    AttributeName=PK,KeyType=HASH \
    AttributeName=SK,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    "[{\"IndexName\":\"GSI1\",\"KeySchema\":[{\"AttributeName\":\"GSI1PK\",\"KeyType\":\"HASH\"},{\"AttributeName\":\"GSI1SK\",\"KeyType\":\"RANGE\"}],\"Projection\":{\"ProjectionType\":\"ALL\"}},{\"IndexName\":\"GSI2\",\"KeySchema\":[{\"AttributeName\":\"GSI2PK\",\"KeyType\":\"HASH\"},{\"AttributeName\":\"GSI2SK\",\"KeyType\":\"RANGE\"}],\"Projection\":{\"ProjectionType\":\"ALL\"}},{\"IndexName\":\"GSI3\",\"KeySchema\":[{\"AttributeName\":\"GSI3PK\",\"KeyType\":\"HASH\"},{\"AttributeName\":\"GSI3SK\",\"KeyType\":\"RANGE\"}],\"Projection\":{\"ProjectionType\":\"ALL\"}}]"
```

---

## T014: Create S3 Bucket (exambuddy-pdfs)

### AWS Console Steps:

1. Navigate to **S3** → **Create bucket**
2. Bucket settings:
   - Bucket name: `exambuddy-pdfs` (must be globally unique, add suffix if needed)
   - Region: `us-east-1` (or your preferred region)
   - ❌ Block all public access (keep private)
3. Bucket versioning:
   - ✅ Enable versioning
4. Default encryption:
   - ✅ Enable (SSE-S3)
5. Create lifecycle rule:
   - Rule name: `expire-old-pdfs`
   - Rule scope: Apply to all objects
   - Lifecycle rule actions: ✅ Expire current versions
   - Days after object creation: **90**

### CLI Alternative:

```bash
aws s3api create-bucket \
  --bucket exambuddy-pdfs \
  --region us-east-1

aws s3api put-bucket-versioning \
  --bucket exambuddy-pdfs \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-lifecycle-configuration \
  --bucket exambuddy-pdfs \
  --lifecycle-configuration '{
    "Rules": [{
      "Id": "expire-old-pdfs",
      "Status": "Enabled",
      "Expiration": {"Days": 90}
    }]
  }'
```

---

## T015: Create S3 Bucket (exambuddy-exports)

### AWS Console Steps:

1. Navigate to **S3** → **Create bucket**
2. Bucket settings:
   - Bucket name: `exambuddy-exports`
   - Region: `us-east-1`
   - ❌ Block all public access
3. Bucket versioning: Optional (not required)
4. Create lifecycle rule:
   - Rule name: `expire-exports`
   - Lifecycle rule actions: ✅ Expire current versions
   - Days: **7**

### CLI Alternative:

```bash
aws s3api create-bucket \
  --bucket exambuddy-exports \
  --region us-east-1

aws s3api put-bucket-lifecycle-configuration \
  --bucket exambuddy-exports \
  --lifecycle-configuration '{
    "Rules": [{
      "Id": "expire-exports",
      "Status": "Enabled",
      "Expiration": {"Days": 7}
    }]
  }'
```

---

## T016: Configure CORS Policy on exambuddy-pdfs

### AWS Console Steps:

1. Navigate to **S3** → `exambuddy-pdfs` → **Permissions** → **CORS**
2. Add CORS configuration:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["PUT", "POST", "GET"],
    "AllowedOrigins": [
      "http://localhost:3000",
      "http://localhost:5173",
      "https://your-production-domain.com"
    ],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

### CLI Alternative:

```bash
cat > cors.json << EOF
{
  "CORSRules": [{
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["PUT", "POST", "GET"],
    "AllowedOrigins": [
      "http://localhost:3000",
      "http://localhost:5173",
      "https://your-production-domain.com"
    ],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }]
}
EOF

aws s3api put-bucket-cors \
  --bucket exambuddy-pdfs \
  --cors-configuration file://cors.json
```

---

## Verification Checklist

After provisioning, verify:

- [ ] Cognito User Pool ID and Client ID added to `.env` files
- [ ] DynamoDB table `exambuddy-main` created with 3 GSIs
- [ ] S3 bucket `exambuddy-pdfs` created with versioning and 90-day expiration
- [ ] S3 bucket `exambuddy-exports` created with 7-day expiration
- [ ] CORS policy configured on `exambuddy-pdfs` bucket
- [ ] IAM role/user has permissions for DynamoDB, S3, and Cognito

## Next Steps

Once AWS resources are provisioned, continue with T017-T030 to implement backend models, services, and frontend foundation.

## CloudFormation Alternative

For infrastructure-as-code, use the CloudFormation template:

```bash
aws cloudformation create-stack \
  --stack-name exambuddy-resources \
  --template-body file://infrastructure/cloudformation-resources.yaml \
  --capabilities CAPABILITY_IAM
```

See `infrastructure/cloudformation-resources.yaml` for full template.

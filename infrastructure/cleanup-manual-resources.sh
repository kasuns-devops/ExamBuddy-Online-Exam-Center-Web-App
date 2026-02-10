#!/bin/bash
# Script to delete manually created AWS resources before switching to automated deployment

set -e

echo "🗑️  Cleaning up manually created AWS resources..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
USER_POOL_ID="eu-north-1_KOieq5GAE"
TABLE_NAME="exambuddy-main"
REGION="eu-north-1"

echo -e "${YELLOW}⚠️  WARNING: This will delete the following resources:${NC}"
echo "  - Cognito User Pool: $USER_POOL_ID"
echo "  - DynamoDB Table: $TABLE_NAME"
echo "  - S3 Buckets: exambuddy-pdfs-*, exambuddy-exports-*"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo "Starting cleanup..."
echo ""

# Delete Cognito User Pool
echo "1️⃣  Deleting Cognito User Pool..."
if aws cognito-idp describe-user-pool --user-pool-id "$USER_POOL_ID" --region "$REGION" &>/dev/null; then
    aws cognito-idp delete-user-pool \
        --user-pool-id "$USER_POOL_ID" \
        --region "$REGION"
    echo -e "${GREEN}✅ Cognito User Pool deleted${NC}"
else
    echo -e "${YELLOW}⚠️  User Pool not found or already deleted${NC}"
fi

# Delete DynamoDB Table
echo ""
echo "2️⃣  Deleting DynamoDB Table..."
if aws dynamodb describe-table --table-name "$TABLE_NAME" --region "$REGION" &>/dev/null; then
    aws dynamodb delete-table \
        --table-name "$TABLE_NAME" \
        --region "$REGION"
    echo -e "${GREEN}✅ DynamoDB Table deletion initiated (takes ~2 minutes)${NC}"
else
    echo -e "${YELLOW}⚠️  Table not found or already deleted${NC}"
fi

# Delete S3 Buckets
echo ""
echo "3️⃣  Deleting S3 Buckets..."

# Find and delete all exambuddy buckets
BUCKETS=$(aws s3api list-buckets --query "Buckets[?starts_with(Name, 'exambuddy-')].Name" --output text --region "$REGION")

if [ -z "$BUCKETS" ]; then
    echo -e "${YELLOW}⚠️  No exambuddy S3 buckets found${NC}"
else
    for bucket in $BUCKETS; do
        echo "  Deleting bucket: $bucket"
        
        # Empty bucket first (required before deletion)
        aws s3 rm "s3://$bucket" --recursive --region "$REGION" 2>/dev/null || true
        
        # Delete bucket
        aws s3api delete-bucket --bucket "$bucket" --region "$REGION" 2>/dev/null || true
        
        echo -e "${GREEN}  ✅ Bucket $bucket deleted${NC}"
    done
fi

echo ""
echo -e "${GREEN}🎉 Cleanup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Set up GitHub Secrets (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)"
echo "  2. Push code to trigger GitHub Actions deployment"
echo "  3. Get new resource IDs from CloudFormation outputs"
echo "  4. Update .env files with new values"

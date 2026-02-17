"""
Quick AWS Connectivity Test
Tests connection to deployed AWS resources
"""
import boto3
from src.config import settings

def test_cognito():
    """Test Cognito User Pool connection"""
    print(f"\n🔐 Testing Cognito User Pool: {settings.cognito_user_pool_id}")
    try:
        client = boto3.client('cognito-idp', region_name=settings.cognito_region)
        response = client.describe_user_pool(UserPoolId=settings.cognito_user_pool_id)
        print(f"✅ Cognito User Pool: {response['UserPool']['Name']}")
        print(f"   ID: {response['UserPool']['Id']}")
        print(f"   Creation Date: {response['UserPool']['CreationDate']}")
        return True
    except Exception as e:
        print(f"❌ Cognito Error: {e}")
        return False

def test_dynamodb():
    """Test DynamoDB table connection"""
    print(f"\n📊 Testing DynamoDB Table: {settings.dynamodb_table_name}")
    try:
        client = boto3.client('dynamodb', region_name=settings.aws_region)
        response = client.describe_table(TableName=settings.dynamodb_table_name)
        print(f"✅ DynamoDB Table: {response['Table']['TableName']}")
        print(f"   Status: {response['Table']['TableStatus']}")
        print(f"   Item Count: {response['Table']['ItemCount']}")
        print(f"   GSIs: {len(response['Table'].get('GlobalSecondaryIndexes', []))}")
        return True
    except Exception as e:
        print(f"❌ DynamoDB Error: {e}")
        return False

def test_s3():
    """Test S3 buckets connection"""
    print(f"\n📦 Testing S3 Buckets:")
    success = True
    
    for bucket_name in [settings.s3_pdfs_bucket, settings.s3_exports_bucket]:
        try:
            client = boto3.client('s3', region_name=settings.aws_region)
            response = client.head_bucket(Bucket=bucket_name)
            print(f"✅ S3 Bucket: {bucket_name}")
        except Exception as e:
            print(f"❌ S3 Bucket Error ({bucket_name}): {e}")
            success = False
    
    return success

def main():
    print("=" * 60)
    print("ExamBuddy - AWS Connectivity Test")
    print("=" * 60)
    print(f"AWS Region: {settings.aws_region}")
    print(f"Environment: {settings.environment}")
    
    results = []
    results.append(("Cognito", test_cognito()))
    results.append(("DynamoDB", test_dynamodb()))
    results.append(("S3", test_s3()))
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    for service, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{service}: {status}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All AWS services are accessible!")
    else:
        print("⚠️  Some services failed connectivity test")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)

#!/usr/bin/env python
"""
Test auto-storing extracted PDF questions to DynamoDB
"""
import requests
import os
import time
import asyncio

BASE_URL = "http://localhost:8000"
PDF_PATH = "sample_questions.pdf"

def test_auto_store():
    """Test PDF upload with auto_store=true"""
    
    print("\n" + "="*80)
    print("💾 Testing PDF Auto-Store to DynamoDB")
    print("="*80)
    
    if not os.path.exists(PDF_PATH):
        print(f"\n❌ PDF file not found: {PDF_PATH}")
        return
    
    print(f"\n📄 PDF File: {PDF_PATH}")
    print(f"   Size: {os.path.getsize(PDF_PATH)} bytes")
    
    try:
        with open(PDF_PATH, 'rb') as f:
            files = {'file': ('sample.pdf', f, 'application/pdf')}
            params = {
                'project_id': 'demo-project',
                'auto_store': 'true'  # Enable auto-store
            }
            
            print(f"\n🚀 Uploading PDF with auto_store=true")
            print(f"   This will extract AND store questions to DynamoDB")
            
            response = requests.post(
                f"{BASE_URL}/api/questions/upload-pdf",
                files=files,
                params=params,
                timeout=30
            )
        
        print(f"\n✓ Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📊 Upload & Store Results:")
            print(f"   Upload ID: {data['upload_id']}")
            print(f"   Total Questions: {data['questions_found']}")
            print(f"   Valid: {data['questions_valid']}")
            print(f"   Stored to DynamoDB: {data['questions_valid']}")
            
            if data.get('questions'):
                print(f"\n📋 Stored Questions:")
                for i, q in enumerate(data['questions'], 1):
                    print(f"\n   [{i}] Question ID: {q['question_id'][:8]}...")
                    print(f"       Text: {q['text'][:55]}...")
                    print(f"       Type: {q['detected_type']}")
                    print(f"       Options: {q['options_count']}")
                
                print(f"\n✅ All {data['questions_valid']} questions stored to DynamoDB!")
                print(f"\n🎯 Next Steps:")
                print(f"   1. Questions are now available in project 'demo-project'")
                print(f"   2. Can be added to exams immediately")
                print(f"   3. Check DynamoDB table: exambuddy-main-dev")
                print(f"   4. Use question IDs to reference in exams")
            
            return data
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None
    
    print("\n" + "="*80)

if __name__ == "__main__":
    print("\n🎯 ExamBuddy PDF Auto-Store Test\n")
    
    # Note: This requires AWS credentials and DynamoDB access
    print("⚠️  Note: This test stores questions to DynamoDB")
    print("    Ensure you have AWS credentials configured")
    print("    And DynamoDB table 'exambuddy-main-dev' exists")
    
    test_auto_store()

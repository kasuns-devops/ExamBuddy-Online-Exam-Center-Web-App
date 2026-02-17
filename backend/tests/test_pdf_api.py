#!/usr/bin/env python
"""Test PDF upload API endpoint"""
import requests
import os
import time

BASE_URL = "http://localhost:8000"
PDF_PATH = "sample_questions.pdf"

def main():
    print("\n" + "="*80)
    print("📤 Testing PDF Upload API Endpoint")
    print("="*80)
    
    # Wait for backend to be ready
    print("\n⏳ Waiting for backend to be ready...")
    max_tries = 10
    for i in range(max_tries):
        try:
            requests.get(f"{BASE_URL}/")
            print("✓ Backend is ready!")
            break
        except:
            if i < max_tries - 1:
                time.sleep(1)
            else:
                print("❌ Backend not responding after 10 seconds")
                return
    
    # Test PDF upload
    print(f"\n📄 PDF File: {PDF_PATH}")
    print(f"   Size: {os.path.getsize(PDF_PATH)} bytes")
    
    try:
        with open(PDF_PATH, 'rb') as f:
            files = {'file': ('sample.pdf', f, 'application/pdf')}
            params = {
                'project_id': 'demo-project',
                'auto_store': 'false'
            }
            
            print(f"\n🚀 Uploading to {BASE_URL}/api/questions/upload-pdf")
            
            response = requests.post(
                f"{BASE_URL}/api/questions/upload-pdf",
                files=files,
                params=params,
                timeout=30
            )
        
        print(f"✓ Status: {response.status_code}\n")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Upload Results:")
            print(f"   Upload ID: {data.get('upload_id', 'N/A')}")
            print(f"   Questions found: {data.get('questions_found', 0)}")
            print(f"   Valid: {data.get('questions_valid', 0)}")
            print(f"   Invalid: {data.get('questions_invalid', 0)}")
            
            if data.get('errors'):
                print(f"\n⚠️  Errors:")
                for err in data['errors']:
                    print(f"   - {err}")
            
            if data.get('questions'):
                print(f"\n📋 Extracted Questions with Auto-Detected Types:")
                for i, q in enumerate(data['questions'], 1):
                    print(f"\n   [{i}] {q['text'][:60]}")
                    print(f"       Type: {q['detected_type']}")
                    print(f"       Options: {q['options_count']}")
                    if q.get('metadata'):
                        print(f"       Metadata: {q['metadata']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

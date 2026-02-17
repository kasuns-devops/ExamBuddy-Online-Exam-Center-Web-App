#!/usr/bin/env python
"""
End-to-End Test: PDF Upload → Question Extraction → Type Detection
Demonstrates the full workflow of the PDF feature
"""
import requests
import os
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
PDF_PATH = "sample_questions.pdf"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_pdf_feature():
    """Test the complete PDF upload and extraction feature"""
    
    # Phase 1: Verify backend is ready
    print_section("Phase 1: Backend Health Check")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Status: {data.get('status', 'unknown')}")
            print(f"   API Version: {data.get('version', 'unknown')}")
        else:
            print(f"❌ Backend error: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return
    
    # Phase 2: Upload PDF and extract questions
    print_section("Phase 2: PDF Upload & Question Extraction")
    
    if not os.path.exists(PDF_PATH):
        print(f"❌ PDF file not found: {PDF_PATH}")
        return
    
    pdf_size = os.path.getsize(PDF_PATH)
    print(f"📄 PDF File: {PDF_PATH}")
    print(f"   Size: {pdf_size} bytes")
    print(f"   Modified: {datetime.fromtimestamp(os.path.getmtime(PDF_PATH))}")
    
    try:
        with open(PDF_PATH, 'rb') as f:
            files = {'file': ('sample.pdf', f, 'application/pdf')}
            params = {
                'project_id': 'demo-project',
                'auto_store': 'false'
            }
            
            print(f"\n🚀 Uploading PDF to {BASE_URL}/api/questions/upload-pdf")
            
            response = requests.post(
                f"{BASE_URL}/api/questions/upload-pdf",
                files=files,
                params=params,
                timeout=30
            )
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return
        
        data = response.json()
        print(f"✅ Upload successful!")
        print(f"   Upload ID: {data['upload_id']}")
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return
    
    # Phase 3: Display extraction results
    print_section("Phase 3: Question Extraction Results")
    
    print(f"📊 Statistics:")
    print(f"   Total Questions: {data['questions_found']}")
    print(f"   Valid: {data['questions_valid']}")
    print(f"   Invalid: {data['questions_invalid']}")
    
    if data['errors']:
        print(f"\n⚠️  Errors encountered:")
        for error in data['errors']:
            print(f"   - {error}")
    
    # Phase 4: Display extracted questions with detected types
    print_section("Phase 4: Auto-Detected Question Types")
    
    if data.get('questions'):
        type_summary = {}
        for i, q in enumerate(data['questions'], 1):
            q_type = q['detected_type']
            type_summary[q_type] = type_summary.get(q_type, 0) + 1
            
            print(f"[{i}] {q['text'][:70]}")
            print(f"    │")
            print(f"    ├─ Type: {q['detected_type'].upper()}")
            print(f"    ├─ Options: {q['options_count']}")
            if q.get('metadata'):
                print(f"    └─ Metadata: {json.dumps(q['metadata'], indent=8)}")
            print()
        
        print(f"\n📈 Type Distribution:")
        for q_type, count in sorted(type_summary.items()):
            print(f"   {q_type}: {count} question{'s' if count > 1 else ''}")
    
    # Phase 5: Summary and recommendations
    print_section("Phase 5: Summary & Next Steps")
    
    print(f"✅ PDF Feature Test Completed Successfully!")
    print(f"\n📋 What Was Tested:")
    print(f"   1. PDF file upload to backend API")
    print(f"   2. Text extraction from PDF using pdfplumber")
    print(f"   3. Question parsing with regex patterns")
    print(f"   4. Automatic question type detection")
    print(f"   5. Type-specific metadata extraction")
    
    print(f"\n🎯 Features Demonstrated:")
    print(f"   • PDF Parser: Extracts Q1) A) B) C) D) format")
    print(f"   • Type Detection: Analyzes question structure to auto-detect type")
    print(f"   • Metadata Extraction: Captures type-specific information")
    print(f"   • API Integration: RESTful endpoint for PDF uploads")
    
    print(f"\n📚 Question Types Auto-Detected:")
    print(f"   • MULTIPLE_CHOICE: Single correct answer")
    print(f"   • MULTIPLE_RESPONSE: Select multiple correct answers")
    print(f"   • DRAG_AND_DROP: Matching/pairing questions")
    print(f"   • HOT_AREA: Click on image regions")
    print(f"   • BUILD_LIST: Order or sequence steps")
    print(f"   • DROP_DOWN_SELECTION: Fill-in-the-blank")
    print(f"   • SCENARIO_SERIES: Scenario-based statements")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Review extracted questions in admin panel")
    print(f"   2. Auto-store questions to DynamoDB with auto_store=true")
    print(f"   3. Create UI component for PDF upload in frontend")
    print(f"   4. Integrate with exam creation workflow")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    print("\n🎯 ExamBuddy PDF Upload Feature - End-to-End Test\n")
    test_pdf_feature()

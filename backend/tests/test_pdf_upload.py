"""
Test PDF upload and question extraction flow
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import requests
import asyncio
from pathlib import Path


async def test_pdf_upload(pdf_path: str, project_id: str = "demo-project-id"):
    """Test PDF upload endpoint"""
    
    BASE_URL = "http://localhost:8000"
    
    print("=" * 60)
    print("🧪 Testing PDF Upload & Question Extraction")
    print("=" * 60)
    
    # Check if PDF exists
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        print("   Creating sample PDF first...")
        from create_sample_pdf import create_sample_pdf
        pdf_path = create_sample_pdf()
    
    print(f"\n📄 PDF File: {pdf_path}")
    print(f"   Size: {os.path.getsize(pdf_path)} bytes")
    
    # Upload PDF
    print(f"\n📤 Uploading to {BASE_URL}/api/questions/upload-pdf...")
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': ('sample.pdf', f, 'application/pdf')}
            params = {
                'project_id': project_id,
                'auto_store': False  # Review first
            }
            
            response = requests.post(
                f"{BASE_URL}/api/questions/upload-pdf",
                files=files,
                params=params,
                timeout=30
            )
        
        print(f"✓ Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📊 Extraction Results:")
            print(f"   Questions found: {data['questions_found']}")
            print(f"   Valid: {data['questions_valid']}")
            print(f"   Invalid: {data['questions_invalid']}")
            
            if data['errors']:
                print(f"\n⚠️  Errors:")
                for error in data['errors']:
                    print(f"   - {error}")
            
            if data['questions']:
                print(f"\n📋 Extracted Questions:")
                for i, q in enumerate(data['questions'], 1):
                    print(f"\n   [{i}] {q['text']}")
                    print(f"       Type: {q['detected_type']}")
                    print(f"       Options: {q['options_count']}")
                    print(f"       Metadata: {q['metadata']}")
            
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed. Is backend running on {BASE_URL}?")
        print(f"   Try: cd backend && python -m uvicorn src.main:app --reload")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def test_pdf_extraction_local():
    """Test PDF extraction locally without API"""
    
    print("\n" + "=" * 60)
    print("🔍 Testing Local PDF Extraction")
    print("=" * 60)
    
    from src.services.pdf_parser import PDFQuestionExtractor, PDFQuestionValidator
    from src.services.question_type_detector import QuestionTypeDetector
    
    # Create sample PDF
    from create_sample_pdf import create_sample_pdf
    pdf_path = create_sample_pdf("test_sample.pdf")
    
    try:
        print(f"\n📄 Extracting from: {pdf_path}")
        
        # Extract questions
        questions = PDFQuestionExtractor.extract_from_file(pdf_path, "demo-project-id")
        print(f"\n✓ Extracted {len(questions)} questions")
        
        # Validate questions
        valid, errors = PDFQuestionValidator.validate_questions(questions)
        print(f"✓ Validated: {len(valid)} valid, {len(errors)} errors")
        
        if errors:
            print(f"\n⚠️  Validation errors:")
            for error in errors:
                print(f"   - {error}")
        
        # Detect types
        print(f"\n🔍 Detecting question types:")
        for i, q in enumerate(valid, 1):
            detected_type, metadata = QuestionTypeDetector.detect_type(q)
            print(f"\n   [{i}] {q.text[:60]}...")
            print(f"       Type: {detected_type}")
            print(f"       Options: {len(q.answer_options)}")
            print(f"       Metadata: {metadata}")
        
        return valid
    
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print(f"   Install: pip install pdfplumber")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if os.path.exists("test_sample.pdf"):
            os.remove("test_sample.pdf")


async def main():
    """Run all tests"""
    
    print("\n🚀 PDF Upload & Question Extraction Test Suite")
    print("=" * 60)
    
    # Test 1: Local extraction (doesn't require server)
    print("\n[Test 1] Local PDF Extraction")
    await test_pdf_extraction_local()
    
    # Test 2: API upload (requires running backend)
    print("\n[Test 2] API Upload Endpoint")
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "..", "sample_questions.pdf")
    if not os.path.exists(pdf_path):
        from create_sample_pdf import create_sample_pdf
        pdf_path = create_sample_pdf(pdf_path)
    
    await test_pdf_upload(pdf_path)
    
    print("\n" + "=" * 60)
    print("✅ Test suite complete!")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python
"""Test PDF extraction and type detection"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.pdf_parser import PDFQuestionExtractor
from src.services.question_type_detector import QuestionTypeDetector
import pdfplumber

def main():
    print("\n🔍 PDF Extraction & Type Detection Test\n")
    print("=" * 80)
    
    # Extract from PDF
    with pdfplumber.open('sample_questions.pdf') as pdf:
        text = ''.join(page.extract_text() or '' for page in pdf.pages)
    
    questions = PDFQuestionExtractor.parse_pdf_text(text, 'demo-project-id')
    print(f"✓ Extracted {len(questions)} questions from PDF\n")
    
    # Display results
    print(f"{'#':<2} | {'Question':<55} | {'Type':<20}")
    print("-" * 80)
    
    for i, q in enumerate(questions, 1):
        detected_type, metadata = QuestionTypeDetector.detect_type(q)
        q_preview = (q.text[:50] + '...') if len(q.text) > 50 else q.text
        type_name = detected_type.value
        print(f"{i:<2} | {q_preview:<55} | {type_name:<20}")
    
    print("\n" + "=" * 80)
    print("✅ PDF extraction and type detection working!")

if __name__ == "__main__":
    main()

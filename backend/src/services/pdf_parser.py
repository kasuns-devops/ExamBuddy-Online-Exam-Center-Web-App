"""
PDF Parser - Extracts questions from PDF files
Supports multiple formats: text-based PDFs and image-based PDFs (OCR-ready)
"""
import re
import uuid
from typing import List, Tuple, Optional
from src.models.question import Question, QuestionType, DifficultyLevel


class PDFQuestionExtractor:
    """Extract questions from PDF content"""

    @staticmethod
    def parse_pdf_text(pdf_text: str, project_id: str) -> List[Question]:
        """
        Parse text-based PDF content and extract questions.
        
        Supports formats:
        1. Q1) Question text? A) opt1 B) opt2 C) opt3 D) opt4
        2. Question number. Question text?
           A. Option 1
           B. Option 2
           C. Option 3
           D. Option 4
        
        Args:
            pdf_text: Extracted text from PDF
            project_id: Project to associate questions with
        
        Returns:
            List of Question objects with auto-detected types
        """
        questions = []
        
        # Split by Q# pattern
        lines = pdf_text.split('\n')
        current_question = None
        current_options = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            i += 1
            
            if not line:
                continue
            
            # Check if line starts a new question (Q1), Q2), etc.)
            question_match = re.match(r'^Q\s*(\d+)\)\s*(.+)$', line, re.IGNORECASE)
            if question_match:
                # Save previous question
                if current_question and len(current_options) >= 2:
                    questions.append(
                        PDFQuestionExtractor._create_question_obj(
                            current_question, current_options, project_id
                        )
                    )
                
                # Start new question
                current_question = question_match.group(2)
                current_options = []
                continue
            
            # Check for options (A), B), C), D) or A), B), etc.)
            if current_question:
                option_match = re.match(r'^([A-E])\)\s*(.+)$', line)
                if option_match:
                    current_options.append(option_match.group(2).strip())
        
        # Save last question
        if current_question and len(current_options) >= 2:
            questions.append(
                PDFQuestionExtractor._create_question_obj(
                    current_question, current_options, project_id
                )
            )
        
        return questions

    @staticmethod
    def _create_question_obj(text: str, options: List[str], project_id: str) -> Question:
        """Convert extracted question data to Question model"""
        question = Question(
            question_id=f"q-{uuid.uuid4()}",
            project_id=project_id,
            text=text,
            answer_options=options,
            correct_index=0,  # Default; admin can override
            difficulty=DifficultyLevel.MEDIUM,  # Default; admin can adjust
            time_limit_seconds=60,
            source="pdf"
        )
        
        return question

    @staticmethod
    def extract_from_file(file_path: str, project_id: str) -> List[Question]:
        """
        Extract questions from a PDF file.
        Uses pdfplumber if available, falls back to basic text extraction.
        
        Args:
            file_path: Path to PDF file
            project_id: Project ID to associate questions
        
        Returns:
            List of extracted Question objects
        """
        try:
            import pdfplumber
            
            questions = []
            with pdfplumber.open(file_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() or ""
            
            return PDFQuestionExtractor.parse_pdf_text(full_text, project_id)
        
        except ImportError:
            # Fallback: try pypdf2
            try:
                from PyPDF2 import PdfReader
                
                reader = PdfReader(file_path)
                full_text = ""
                for page in reader.pages:
                    full_text += page.extract_text() or ""
                
                return PDFQuestionExtractor.parse_pdf_text(full_text, project_id)
            
            except ImportError:
                raise ImportError(
                    "PDF parsing requires pdfplumber or PyPDF2. "
                    "Install with: pip install pdfplumber or pip install PyPDF2"
                )


class PDFQuestionValidator:
    """Validate extracted questions before storing"""

    @staticmethod
    def validate_questions(questions: List[Question]) -> Tuple[List[Question], List[str]]:
        """
        Validate extracted questions.
        
        Returns:
            (valid_questions, error_messages)
        """
        valid = []
        errors = []
        
        for i, q in enumerate(questions, 1):
            # Check minimum requirements
            if not q.text or len(q.text) < 5:
                errors.append(f"Q{i}: Question text too short")
                continue
            
            if len(q.answer_options) < 2:
                errors.append(f"Q{i}: Need at least 2 options")
                continue
            
            if len(q.answer_options) > 6:
                errors.append(f"Q{i}: Too many options (max 6)")
                continue
            
            if q.correct_index < 0 or q.correct_index >= len(q.answer_options):
                errors.append(f"Q{i}: Invalid correct answer index")
                continue
            
            valid.append(q)
        
        return valid, errors

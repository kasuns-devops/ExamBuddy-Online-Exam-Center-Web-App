"""
Create test questions in DynamoDB for testing the exam flow
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.question import Question, DifficultyLevel
from src.database.dynamodb_client import DynamoDBClient
from src.services.question_type_detector import QuestionTypeDetector
from datetime import datetime
import uuid
import asyncio

async def create_test_questions():
    """Create sample questions for testing with auto-detected types"""
    client = DynamoDBClient()
    
    project_id = "demo-project-id"
    
    questions_data = [
        {
            "text": "What is the capital of France?",
            "answer_options": ["London", "Paris", "Berlin", "Madrid"],
            "correct_index": 1,
            "difficulty": DifficultyLevel.EASY,
        },
        {
            "text": "What is 15 + 27?",
            "answer_options": ["40", "41", "42", "43"],
            "correct_index": 2,
            "difficulty": DifficultyLevel.EASY,
        },
        {
            "text": "Which planet is known as the Red Planet?",
            "answer_options": ["Venus", "Mars", "Jupiter", "Saturn"],
            "correct_index": 1,
            "difficulty": DifficultyLevel.EASY,
        },
        {
            "text": "What is the chemical symbol for gold?",
            "answer_options": ["Go", "Gd", "Au", "Ag"],
            "correct_index": 2,
            "difficulty": DifficultyLevel.MEDIUM,
        },
        {
            "text": "Who wrote 'Romeo and Juliet'?",
            "answer_options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
            "correct_index": 1,
            "difficulty": DifficultyLevel.EASY,
        },
        {
            "text": "What is the speed of light in vacuum?",
            "answer_options": ["299,792 km/s", "150,000 km/s", "500,000 km/s", "1,000,000 km/s"],
            "correct_index": 0,
            "difficulty": DifficultyLevel.MEDIUM,
        },
        {
            "text": "Select all that apply: Which of these are programming languages?",
            "answer_options": ["Python", "Azure", "Java", "SQL", "Portal"],
            "correct_index": 0,
            "difficulty": DifficultyLevel.MEDIUM,
        },
        {
            "text": "Arrange the following steps in correct order: 1. Install Python, 2. Write code, 3. Run script",
            "answer_options": ["1. Install Python", "2. Write code", "3. Run script"],
            "correct_index": 0,
            "difficulty": DifficultyLevel.MEDIUM,
        },
        {
            "text": "In which year did World War II end?",
            "answer_options": ["1943", "1944", "1945", "1946"],
            "correct_index": 2,
            "difficulty": DifficultyLevel.MEDIUM,
        },
        {
            "text": "What is the square root of 144?",
            "answer_options": ["10", "11", "12", "13"],
            "correct_index": 2,
            "difficulty": DifficultyLevel.EASY,
        }
    ]
    
    print(f"Creating {len(questions_data)} test questions with auto-detected types...")
    
    for i, q_data in enumerate(questions_data, 1):
        # Create Question model
        question = Question(
            question_id=str(uuid.uuid4()),
            project_id=project_id,
            text=q_data["text"],
            answer_options=q_data["answer_options"],
            correct_index=q_data["correct_index"],
            difficulty=q_data["difficulty"],
            time_limit_seconds=60,
            source="manual"
        )
        
        # Auto-detect type
        detected_type, metadata = QuestionTypeDetector.detect_type(question)
        question.question_type = detected_type
        question.metadata = metadata
        
        # Create DynamoDB item
        item = question.to_dynamodb_item()
        
        await client.put_item(item)
        print(f"  [{i}/{len(questions_data)}] ✓ {question.text[:40]}... [{detected_type}]")
        {
            "question_id": str(uuid.uuid4()),
            "project_id": project_id,
            "question_text": "Which programming language is known for its use in data science?",
            "options": ["Java", "C++", "Python", "Assembly"],
            "correct_answer": 2,
            "difficulty": "easy",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
        {
            "question_id": str(uuid.uuid4()),
            "project_id": project_id,
            "question_text": "What is the largest ocean on Earth?",
            "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
            "correct_answer": 3,
            "difficulty": "easy",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        },
    
    print(f"\n✅ Successfully created {len(questions_data)} questions!")
    print(f"📋 Project ID: {project_id}")
    print(f"🔍 You can now start an exam with this project ID")

if __name__ == "__main__":
    asyncio.run(create_test_questions())

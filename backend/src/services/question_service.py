"""
Question Service - Business logic for question management
"""
import random
from typing import List, Optional
from src.models.question import Question, DifficultyLevel
from src.database.dynamodb_client import DynamoDBClient
from src.services.question_type_detector import QuestionTypeDetector


class QuestionService:
    """Service for question-related operations"""
    
    def __init__(self):
        self.db = DynamoDBClient()
    
    async def random_select_questions(
        self,
        project_id: str,
        count: int,
        difficulty: Optional[DifficultyLevel] = None
    ) -> List[Question]:
        """
        Randomly select questions from a project's question bank.
        
        Args:
            project_id: Project identifier
            count: Number of questions to select
            difficulty: Optional difficulty filter (easy, medium, hard, expert)
        
        Returns:
            List of randomly selected Question objects
        
        Raises:
            ValueError: If not enough questions available in the project
        """
        # Query all questions for the project from DynamoDB
        # PK: PROJECT#{project_id}, SK: QUESTION#*
        questions_data = await self.db.query(
            key_condition_expression='PK = :pk AND begins_with(SK, :sk_prefix)',
            expression_attribute_values={
                ':pk': f'PROJECT#{project_id}',
                ':sk_prefix': 'QUESTION#'
            }
        )
        
        # Filter by difficulty if specified
        if difficulty:
            questions_data = [
                q for q in questions_data 
                if q.get('difficulty') == difficulty.value
            ]
        
        # Check if enough questions available
        if len(questions_data) < count:
            raise ValueError(
                f"Not enough questions available. Requested: {count}, Available: {len(questions_data)}"
            )
        
        # Randomly select questions
        selected_data = random.sample(questions_data, count)
        
        # Convert to Question models - handle both old and new field names
        questions = []
        for q in selected_data:
            try:
                question = Question(
                    question_id=q['question_id'],
                    project_id=q['project_id'],
                    text=q.get('text') or q.get('question_text', ''),
                    answer_options=q.get('answer_options') or q.get('options', []),
                    correct_index=q.get('correct_index') or q.get('correct_answer', 0),
                    difficulty=q.get('difficulty', 'medium'),
                    time_limit_seconds=q.get('time_limit_seconds', 60),
                    created_at=q.get('created_at', ''),
                    source=q.get('source', 'manual'),
                    tags=q.get('tags')
                )
                questions.append(question)
            except Exception as e:
                # If model validation fails, keep as dict
                questions.append(q)
        
        return questions
    
    async def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """
        Retrieve a specific question by ID.
        
        Args:
            question_id: Question identifier
        
        Returns:
            Question object if found, None otherwise
        """
        # Query DynamoDB for the question
        # We need to search across all projects using GSI
        results = await self.db.query(
            key_condition_expression='GSI1PK = :pk',
            expression_attribute_values={
                ':pk': f'QUESTION#{question_id}'
            },
            index_name='GSI1',
            limit=1
        )
        
        if not results:
            return None
        
        return Question(**results[0])
    
    async def get_questions_by_ids(self, question_ids: List[str]) -> List[Question]:
        """
        Retrieve multiple questions by their IDs.
        
        Args:
            question_ids: List of question identifiers
        
        Returns:
            List of Question objects
        """
        questions = []
        for qid in question_ids:
            question = await self.get_question_by_id(qid)
            if question:
                questions.append(question)
        
        return questions
    
    async def create_question(self, question: Question, auto_detect_type: bool = True) -> Question:
        """
        Create a new question in the database.
        
        Args:
            question: Question object to create
            auto_detect_type: If True, auto-detect question type from structure
        
        Returns:
            Created Question object
        """
        # Auto-detect question type if enabled
        if auto_detect_type:
            detected_type, metadata = QuestionTypeDetector.detect_type(question)
            question.question_type = detected_type
            if question.metadata:
                question.metadata.update(metadata)
            else:
                question.metadata = metadata
        
        # Store in DynamoDB
        item = {
            'PK': f'PROJECT#{question.project_id}',
            'SK': f'QUESTION#{question.question_id}',
            'GSI1PK': f'QUESTION#{question.question_id}',
            'GSI1SK': f'PROJECT#{question.project_id}',
            **question.dict()
        }
        
        await self.db.put_item(item)
        return question
    
    async def update_question(
        self,
        question_id: str,
        updates: dict
    ) -> Optional[Question]:
        """
        Update an existing question.
        
        Args:
            question_id: Question identifier
            updates: Dictionary of fields to update
        
        Returns:
            Updated Question object if found, None otherwise
        """
        # Get existing question first
        question = await self.get_question_by_id(question_id)
        if not question:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(question, key):
                setattr(question, key, value)
        
        # Save to database
        await self.create_question(question)
        return question
    
    async def delete_question(self, project_id: str, question_id: str) -> bool:
        """
        Delete a question from the database.
        
        Args:
            project_id: Project identifier
            question_id: Question identifier
        
        Returns:
            True if deleted successfully, False otherwise
        """
        await self.db.delete_item(
            pk=f'PROJECT#{project_id}',
            sk=f'QUESTION#{question_id}'
        )
        return True

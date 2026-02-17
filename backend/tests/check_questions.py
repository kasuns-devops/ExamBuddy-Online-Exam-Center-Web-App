"""
Verify questions in DynamoDB
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import asyncio
from src.database.dynamodb_client import DynamoDBClient

async def check_questions():
    client = DynamoDBClient()
    project_id = "demo-project-id"
    
    print(f"Checking questions for project: {project_id}")
    
    # Query questions
    questions = await client.query(
        key_condition_expression='PK = :pk AND begins_with(SK, :sk_prefix)',
        expression_attribute_values={
            ':pk': f'PROJECT#{project_id}',
            ':sk_prefix': 'QUESTION#'
        }
    )
    
    print(f"\nFound {len(questions)} questions:")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q.get('question_text', 'N/A')[:50]}...")
        print(f"     Difficulty: {q.get('difficulty')}")
        print(f"     Options: {len(q.get('options', []))} choices")

if __name__ == "__main__":
    asyncio.run(check_questions())

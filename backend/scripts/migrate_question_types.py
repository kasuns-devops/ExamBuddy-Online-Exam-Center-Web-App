"""
Migration script to auto-categorize existing questions
Scans all questions and assigns detected types + metadata
"""
import asyncio
import sys
from src.database.dynamodb_client import DynamoDBClient
from src.models.question import Question
from src.services.question_type_detector import QuestionTypeUpdater


async def migrate_questions_to_typed():
    """
    Scan all questions in DynamoDB and auto-detect their types.
    Updates each question with detected type and metadata.
    """
    db = DynamoDBClient()
    table_name = "exambuddy-main-dev"
    
    print("🔍 Starting question type migration...")
    print(f"📚 Table: {table_name}")
    
    # Scan for all question items
    scan_kwargs = {
        'FilterExpression': 'entity_type = :et',
        'ExpressionAttributeValues': {':et': 'question'}
    }
    
    processed = 0
    updated = 0
    errors = 0
    
    try:
        # Get DynamoDB table
        table = db.dynamodb.Table(table_name)
        
        # Paginated scan
        paginator = db.dynamodb_resource.meta.client.get_paginator('scan')
        page_iterator = paginator.paginate(TableName=table_name, **scan_kwargs)
        
        for page in page_iterator:
            items = page.get('Items', [])
            
            for item in items:
                processed += 1
                try:
                    # Convert to Question model
                    question = Question.from_dynamodb_item(item)
                    
                    # Skip if already has a type (don't overwrite manual assignments)
                    if item.get('question_type') and item.get('question_type') != 'multiple_choice':
                        print(f"✓ Q{processed}: {question.question_id[:8]}... already typed as {item.get('question_type')}")
                        continue
                    
                    # Auto-detect type
                    updated_question = await QuestionTypeUpdater.update_question_type(question)
                    
                    # Prepare DynamoDB item for update
                    db_item = updated_question.to_dynamodb_item()
                    
                    # Update in DynamoDB
                    table.put_item(Item=db_item)
                    
                    updated += 1
                    print(f"✓ Q{processed}: {question.question_id[:8]}... → {updated_question.question_type}")
                    
                except Exception as e:
                    errors += 1
                    print(f"✗ Q{processed}: Failed - {str(e)[:60]}")
        
        print("\n" + "=" * 60)
        print(f"✅ Migration complete!")
        print(f"   Scanned: {processed}")
        print(f"   Updated: {updated}")
        print(f"   Errors: {errors}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(migrate_questions_to_typed())

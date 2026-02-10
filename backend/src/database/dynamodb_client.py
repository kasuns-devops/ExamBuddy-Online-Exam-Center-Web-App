"""
DynamoDB Client - Handles all DynamoDB operations for ExamBuddy
"""
import boto3
from botocore.exceptions import ClientError
from typing import Dict, List, Optional, Any
from src.config import settings


class DynamoDBClient:
    """DynamoDB client with helper methods for common operations"""
    
    def __init__(self):
        """Initialize DynamoDB client with configuration from settings"""
        dynamodb_config = {
            'region_name': settings.aws_region
        }
        
        # Use local endpoint for development
        if settings.dynamodb_endpoint:
            dynamodb_config['endpoint_url'] = settings.dynamodb_endpoint
            dynamodb_config['aws_access_key_id'] = 'test'
            dynamodb_config['aws_secret_access_key'] = 'test'
        
        self.client = boto3.client('dynamodb', **dynamodb_config)
        self.resource = boto3.resource('dynamodb', **dynamodb_config)
        self.table = self.resource.Table(settings.dynamodb_table_name)
    
    async def put_item(self, item: Dict[str, Any]) -> bool:
        """
        Put an item into DynamoDB table
        
        Args:
            item: Dictionary representing the item to store
            
        Returns:
            bool: True if successful
        """
        try:
            self.table.put_item(Item=item)
            return True
        except ClientError as e:
            print(f"Error putting item: {e}")
            raise
    
    async def get_item(self, pk: str, sk: str) -> Optional[Dict[str, Any]]:
        """
        Get an item by primary key
        
        Args:
            pk: Partition key value
            sk: Sort key value
            
        Returns:
            Item dict or None if not found
        """
        try:
            response = self.table.get_item(
                Key={'PK': pk, 'SK': sk}
            )
            return response.get('Item')
        except ClientError as e:
            print(f"Error getting item: {e}")
            return None
    
    async def query(
        self,
        key_condition_expression: str,
        expression_attribute_values: Dict[str, Any],
        index_name: Optional[str] = None,
        filter_expression: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query DynamoDB table or GSI
        
        Args:
            key_condition_expression: Query condition (e.g., 'PK = :pk AND begins_with(SK, :sk_prefix)')
            expression_attribute_values: Values for placeholders (e.g., {':pk': 'USER#123', ':sk_prefix': 'PROJECT#'})
            index_name: GSI name if querying an index (e.g., 'GSI1')
            filter_expression: Optional filter expression
            limit: Maximum number of items to return
            
        Returns:
            List of items matching the query
        """
        try:
            query_params = {
                'KeyConditionExpression': key_condition_expression,
                'ExpressionAttributeValues': expression_attribute_values
            }
            
            if index_name:
                query_params['IndexName'] = index_name
            if filter_expression:
                query_params['FilterExpression'] = filter_expression
            if limit:
                query_params['Limit'] = limit
            
            response = self.table.query(**query_params)
            return response.get('Items', [])
        except ClientError as e:
            print(f"Error querying: {e}")
            raise
    
    async def update_item(
        self,
        pk: str,
        sk: str,
        update_expression: str,
        expression_attribute_values: Dict[str, Any],
        expression_attribute_names: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing item
        
        Args:
            pk: Partition key
            sk: Sort key
            update_expression: Update expression (e.g., 'SET #name = :name, #score = :score')
            expression_attribute_values: Values for placeholders
            expression_attribute_names: Name placeholders for reserved words
            
        Returns:
            Updated item attributes
        """
        try:
            update_params = {
                'Key': {'PK': pk, 'SK': sk},
                'UpdateExpression': update_expression,
                'ExpressionAttributeValues': expression_attribute_values,
                'ReturnValues': 'ALL_NEW'
            }
            
            if expression_attribute_names:
                update_params['ExpressionAttributeNames'] = expression_attribute_names
            
            response = self.table.update_item(**update_params)
            return response.get('Attributes', {})
        except ClientError as e:
            print(f"Error updating item: {e}")
            raise
    
    async def delete_item(self, pk: str, sk: str) -> bool:
        """
        Delete an item from the table
        
        Args:
            pk: Partition key
            sk: Sort key
            
        Returns:
            bool: True if successful
        """
        try:
            self.table.delete_item(Key={'PK': pk, 'SK': sk})
            return True
        except ClientError as e:
            print(f"Error deleting item: {e}")
            raise
    
    async def batch_write(self, items: List[Dict[str, Any]]) -> bool:
        """
        Batch write multiple items (max 25 per batch)
        
        Args:
            items: List of items to write
            
        Returns:
            bool: True if successful
        """
        try:
            with self.table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)
            return True
        except ClientError as e:
            print(f"Error batch writing: {e}")
            raise


# Global client instance
dynamodb_client = DynamoDBClient()

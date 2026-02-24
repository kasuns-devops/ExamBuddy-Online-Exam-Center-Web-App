"""
Raw Lambda handler with CORS support - bypasses FastAPI for performance
"""

def lambda_handler(event, context):
    """
    Direct Lambda handler that returns CORS headers
    Handles both OPTIONS preflight and regular requests
    """
    http_method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
    path = event.get('requestContext', {}).get('http', {}).get('path', '/')
    
    # Handle OPTIONS preflight
    if http_method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Max-Age': '3600',
            },
            'body': ''
        }
    
    # Handle GET / (health check)
    if http_method == 'GET' and path == '/':
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            },
            'body': '{"message": "ExamBuddy API", "status": "healthy"}'
        }
    
    # 404 for other paths
    return {
        'statusCode': 404,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json',
        },
        'body': '{"error": "Not found"}'
    }

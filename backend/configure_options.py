#!/usr/bin/env python
"""Configure OPTIONS method for CORS in API Gateway"""
import subprocess
import sys

# Get resource ID
result = subprocess.run([
    'aws', 'apigateway', 'get-resources',
    '--rest-api-id', 'ugx3jtet03',
    '--region', 'eu-north-1',
    '--query', 'items[?path==`/`].id',
    '--output', 'text'
], capture_output=True, text=True)

if result.returncode != 0:
    print(f"Error getting resource: {result.stderr}")
    sys.exit(1)

resource_id = result.stdout.strip()
print(f"Resource ID: {resource_id}")

# Configure integration response
response_params = {
    'method.response.header.Access-Control-Allow-Origin': "'*'",
    'method.response.header.Access-Control-Allow-Methods': "'GET,POST,PUT,DELETE,OPTIONS'",
    'method.response.header.Access-Control-Allow-Headers': "'Content-Type,Authorization'"
}

params_str = ','.join([f'{k}={v}' for k, v in response_params.items()])

print(f"Parameters: {params_str}")

result = subprocess.run([
    'aws', 'apigateway', 'put-integration-response',
    '--rest-api-id', 'ugx3jtet03',
    '--resource-id', resource_id,
    '--http-method', 'OPTIONS',
    '--status-code', '200',
    '--response-parameters', params_str,
    '--region', 'eu-north-1'
], capture_output=True, text=True)

if result.returncode == 0:
    print('✓ OPTIONS integration response configured')
else:
    print(f'Error: {result.stderr}')
    sys.exit(1)

# Deploy the API
print('\nDeploying API Gateway...')
result = subprocess.run([
    'aws', 'apigateway', 'create-deployment',
    '--rest-api-id', 'ugx3jtet03',
    '--stage-name', 'prod',
    '--description', 'Fix CORS for OPTIONS method',
    '--region', 'eu-north-1',
    '--query', 'id',
    '--output', 'text'
], capture_output=True, text=True)

if result.returncode == 0:
    deployment_id = result.stdout.strip()
    print(f'✓ API deployed: {deployment_id}')
else:
    print(f'Error deploying: {result.stderr}')
    sys.exit(1)

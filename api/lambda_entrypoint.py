"""
This module provides AWS Lambda handlers for the document image translation API.
It supports generating presigned S3 URLs for uploads, recording upload status in DynamoDB,
and retrieving the status of uploaded files.
"""

import boto3
import os
import json
import ulid
import re
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name = os.environ.get("STATUS_TABLE_NAME"))
bucket = os.environ['S3_BUCKET']

def sanitize_filename(filename):
    """Sanitize a filename by removing non-alphanumeric characters from the name part.

    Args:
        filename (str): The original filename.

    Returns:
        str: The sanitized filename with only alphanumeric characters in the name part.
    """
    name, ext = os.path.splitext(filename)
    cleaned = re.sub(r'[^A-Za-z0-9]', '', name)
    return f"{cleaned}{ext}"

def lambda_handler(event, context):
    """AWS Lambda handler for document image translation API.

    Handles presigned URL generation, upload status recording, and status retrieval.

    Args:
        event (dict): The event dict from AWS Lambda, containing request data.
        context (LambdaContext): The runtime information provided by AWS Lambda.

    Returns:
        dict: The HTTP response with status code and body.
    """
    path = event['path']
    method = event['httpMethod']

    if path == '/presigned-url' and method == 'GET':
        query = event['queryStringParameters']
        file_name = sanitize_filename(query['file_name'])
        target_lang = query['target_language']
        file_uuid = str(ulid.new())
        key = f"uploads/{file_uuid}/{target_lang}/{file_name}"
        url = s3.generate_presigned_url(
            'put_object',
            Params={'Bucket': bucket, 'Key': key, 'ContentType': 'application/octet-stream'},
            ExpiresIn=3600
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'upload_url': url, 'uuid': file_uuid, 's3_key': key})
        }

    elif path == '/upload-image' and method == 'POST':
        body = json.loads(event['body'])
        uuid_ = body['uuid']
        file_name = sanitize_filename(body['file_name'])
        target_lang = body['target_language']
        status = {
            'uuid': uuid_,
            'file_name': file_name,
            'target_language': target_lang,
            'status': 'uploaded',
            'updated_at': datetime.utcnow().isoformat()
        }
        table.put_item(Item=status)
        return {'statusCode': 200, 'body': json.dumps({'message': 'File status recorded'})}

    elif path == '/status' and method == 'GET':
        query = event['queryStringParameters']
        uuid_ = query['uuid']
        file_name = sanitize_filename(query['file_name'])
        resp = table.get_item(Key={'uuid': uuid_, 'file_name': file_name})
        item = resp.get('Item', {})
        return {
            'statusCode': 200,
            'body': json.dumps(item)
        }

    return {'statusCode': 404, 'body': 'Not Found'}
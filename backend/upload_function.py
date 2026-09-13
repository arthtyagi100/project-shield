import json
import os
import boto3

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))
    try:
        # Check if event or body is completely missing/None
        if not event or 'body' not in event or event['body'] is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Request body is missing or None"})
            }
        
        body_string = event['body']
        
        # Handle if body is already parsed as a dict (from console test events)
        if isinstance(body_string, dict):
            body = body_string
        elif isinstance(body_string, str):
            body = json.loads(body_string)
        else:
            body = {}

        # Safely grab the filename
        filename = body.get('filename')
        
        if not filename:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "filename is required"})
            }

        # Check environment variable
        bucket_name = os.environ.get('UPLOAD_BUCKET_NAME')
        if not bucket_name:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "UPLOAD_BUCKET_NAME environment variable is not configured in Lambda"})
            }

        # Generate the S3 Presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': filename
            },
            ExpiresIn=300
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"uploadUrl": presigned_url})
        }

    except Exception as e:
        print(f"Exception caught: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

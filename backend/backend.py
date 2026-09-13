import os
import boto3


# Initialize AWS clients outside the handler for connection reuse
comprehend = boto3.client('comprehend', region_name='eu-central-1')
s3_client = boto3.client('s3')


def lambda_handler(event, context):
    try:
        # 1. Extract bucket name and file key from the S3 event trigger
        record = event['Records'][0]
        input_bucket = record['s3']['bucket']['name']
        file_key = record['s3']['object']['key']
        
        print(f"Processing file '{file_key}' from bucket '{input_bucket}'")
        
        # 2. Download the uploaded document from S3 to Lambda's temporary storage (/tmp)
        download_path = f"/tmp/{file_key.split('/')[-1]}"
        s3_client.download_file(input_bucket, file_key, download_path)
        
        # 3. Read the text content of the document
        with open(download_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
            
        if not text_content.strip():
            print("The uploaded file is empty.")
            return {"status": "Skipped", "reason": "Empty file"}

        # 4. Call Amazon Comprehend to detect PII entities
        response = comprehend.detect_pii_entities(
            Text=text_content,
            LanguageCode='en'
        )
        
        entities = response.get('Entities', [])
        print(f"Detected {len(entities)} PII entities.")
        
        # 5. Redact the text from back to front to avoid character shifting errors
        sorted_entities = sorted(entities, key=lambda k: k['BeginOffset'], reverse=True)
        redacted_text = text_content
        
        for entity in sorted_entities:
            start = entity['BeginOffset']
            end = entity['EndOffset']
            entity_type = entity['Type'] # e.g., NAME, EMAIL, PHONE, ADDRESS
            
            # Replace sensitive text string with a tag placeholder
            redacted_text = redacted_text[:start] + f"[{entity_type}]" + redacted_text[end:]
            
        # 6. Save the redacted text locally to /tmp
        output_file_name = f"redacted-{file_key.split('/')[-1]}"
        output_path = f"/tmp/{output_file_name}"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(redacted_text)
            
        # 7. Upload the redacted document to your Output S3 Bucket using Environment Variables
        output_bucket = os.environ['OUTPUT_BUCKET_NAME']
        s3_client.upload_file(output_path, output_bucket, output_file_name)
        
        print(f"Successfully saved redacted file to {output_bucket}/{output_file_name}")
        
        return {
            "status": "Success",
            "input_file": file_key,
            "output_file": output_file_name
        }

    except Exception as e:
        print(f"Error processing document: {str(e)}")
        raise e

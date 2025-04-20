import boto3
import logging
import uuid
import time
from fastapi.responses import StreamingResponse
from botocore.exceptions import ClientError
from fastapi import HTTPException

# Using LocalStack endpoint
localstack_endpoint = "http://localhost:4566"
region_name = 'us-west-2'
key_id = "dummy"
access_key = "dummy"

s3 = boto3.client(
    's3',
    region_name=region_name,
    endpoint_url=localstack_endpoint,
    aws_access_key_id=key_id,
    aws_secret_access_key=access_key
)

dynamo = boto3.resource(
    'dynamodb',
    region_name=region_name,
    endpoint_url=localstack_endpoint,
    aws_access_key_id=key_id,
    aws_secret_access_key=access_key
)


bucket_name = "user-uploads"
table = dynamo.Table("uploads-metadata")

def upload_image_to_s3(file):
    #generate unique filename
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    try:
        s3.upload_fileobj(file.file, bucket_name, unique_filename)
        logging.info("successfully uploaded file to S3 bucket")
        return f"https://{bucket_name}.s3.amazonaws.com/{unique_filename}", unique_filename
    except Exception as e:
        logging.error(f"file upload failed for the file:{unique_filename} with error", e)

def save_metadata_to_dynamo(user_id, filename, image_url, description, tags):
    item = {
        "id": str(uuid.uuid4()),
        "filename": filename,
        "user_id": user_id,
        "image_url": image_url,
        "description": description,
        "tags": tags,
        "timestamp": int(time.time())
    }
    try:
        table.put_item(Item=item)
        logging.info("successfully uploaded file metadata to ddb")
    except Exception as e:
        logging.error(f'failed to updated image details in ddb', e)

def list_images_from_dynamo(user_id=None, tag=None):
    scan_kwargs = {}

    if user_id and tag:
        scan_kwargs['FilterExpression'] = "user_id = :u AND contains(tags, :t)"
        scan_kwargs['ExpressionAttributeValues'] = {":u": user_id, ":t": tag}
    elif user_id:
        scan_kwargs['FilterExpression'] = "user_id = :u"
        scan_kwargs['ExpressionAttributeValues'] = {":u": user_id}
    elif tag:
        scan_kwargs['FilterExpression'] = "contains(tags, :t)"
        scan_kwargs['ExpressionAttributeValues'] = {":t": tag}

    response = table.scan(**scan_kwargs) if scan_kwargs else table.scan()
    return response.get('Items', [])


def get_image_from_s3(filename):
    try:
        response = s3.get_object(Bucket=bucket_name, Key=filename)
        return StreamingResponse(response['Body'], media_type="image/jpeg")
    except ClientError:
        raise HTTPException(status_code=404, detail="Image not found")


def delete_image(filename):
    # Delete from S3
    try:
        resp = s3.delete_object(Bucket=bucket_name, Key=filename)
    except Exception as e:
        logging.error(f'Unable to delete file from S3 bucket', e)

    # Fetch the corresponding item to get the ID
    response = table.scan(
        FilterExpression="filename = :f",
        ExpressionAttributeValues={":f": filename}
    )
    items = response.get("Items", [])
    
    if not items:
        raise HTTPException(status_code=404, detail="Metadata not found")

    # Use the ID to delete the metadata
    item_id = items[0]["id"]
    try:
        table.delete_item(Key={"id": item_id})
    except Exception as e:
        logging.error(f'Unable to delete file metadata from ddb', e)
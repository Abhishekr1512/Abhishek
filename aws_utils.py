import boto3
import uuid
import time
from fastapi.responses import StreamingResponse
from botocore.exceptions import ClientError
from fastapi import HTTPException

s3 = boto3.client('s3', region_name='us-east-1')
dynamo = boto3.resource('dynamodb', region_name='us-east-1')
bucket_name = "dummy-s3-bucket"
table = dynamo.Table("InstaImagesMetadata")

def upload_image_to_s3(file):
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    s3.upload_fileobj(file.file, bucket_name, unique_filename)
    return f"https://{bucket_name}.s3.amazonaws.com/{unique_filename}"

def save_metadata_to_dynamo(user_id, filename, image_url, caption, tags):
    item = {
        "filename": filename,
        "user_id": user_id,
        "image_url": image_url,
        "caption": caption,
        "tags": tags,
        "timestamp": int(time.time())
    }
    table.put_item(Item=item)

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
    s3.delete_object(Bucket=bucket_name, Key=filename)
    table.delete_item(Key={"filename": filename})
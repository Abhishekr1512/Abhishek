import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from aws_utils import upload_image_to_s3, save_metadata_to_dynamo, list_images_from_dynamo, get_image_from_s3, delete_image
from models import ImageUploadResponse, ImageMetadata, DeleteResponse
from typing import Optional, List

#to validate specific image format
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg"}

router = APIRouter()

#API to upload image
@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    description: str = Form(""),
    tags: str = Form("")
):
    
    #throw excpetion if filetype doesn't matches
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use png, jpg or jpeg.")

    image_url, unique_filename = upload_image_to_s3(file)
    logging.info(f'file upload successful to the S3 bucket: {unique_filename}')
    save_metadata_to_dynamo(user_id, unique_filename, image_url, description, tags)
    logging.info(f'file metadata upload successful to the ddb table: {unique_filename}')
    return {"message": "Upload successful", "image_url": image_url}

@router.get("/images", response_model=List[ImageMetadata])
def list_images(user_id: Optional[str] = Query(None), tag: Optional[str] = Query(None)):
    return list_images_from_dynamo(user_id=user_id, tag=tag)

@router.get("/image/{filename}")
def view_image(filename: str):
    return get_image_from_s3(filename)

@router.delete("/image/{filename}", response_model=DeleteResponse)
def delete(filename: str):
    delete_image(filename)
    return {"message": f"{filename} deleted successfully"}
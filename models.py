from pydantic import BaseModel, HttpUrl
from typing import Optional

class ImageMetadata(BaseModel):
    filename: str
    user_id: str
    image_url: HttpUrl
    description: Optional[str] = ""
    tags: Optional[str]
    timestamp: Optional[int]

class ImageUploadResponse(BaseModel):
    message: str
    image_url: HttpUrl

class DeleteResponse(BaseModel):
    message: Optional[str] = ""
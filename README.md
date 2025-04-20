# Instagram-like Image Upload Service

## Features
- Upload image and metadata to AWS S3 and DynamoDB
- Filter images by user or tags
- View or download images
- Delete images

## API Endpoints

### POST /api/upload
**Form Data:**
- file: image file
- user_id: string
- description: string
- tags: comma-separated string

### GET /api/images
**Query Parameters (optional):**
- user_id
- tag

### GET /api/image/{filename}

### DELETE /api/image/{filename}

## Local Setup
```bash
pip install -r requirements.txt
python main.py
```

## Run Tests
```bash
pytest
```
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
from datetime import datetime

from ..database import get_db
from ..models import VideoFile
from ..utils.encryption import encryption_manager
from ..services.kafka_service import kafka_service

router = APIRouter()

# Allowed video file types (including encrypted files)
ALLOWED_VIDEO_TYPES = {
    "video/mp4", "video/avi", "video/mov", "video/wmv", 
    "video/flv", "video/webm", "video/mkv", "video/m4v",
    "application/octet-stream"  # For encrypted files
}

# Maximum file size (100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024

@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    encryption_key: str = None,
    db: Session = Depends(get_db)
):
    """
    Upload an encrypted video file.
    The file should be encrypted on the client side before upload.
    """
    
    # Validate file type
    allowed_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file.content_type not in ALLOWED_VIDEO_TYPES and file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_VIDEO_TYPES)} or extensions: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size
    file_size = 0
    file_content = b""
    
    # Read file content
    while chunk := await file.read(8192):
        file_size += len(chunk)
        file_content += chunk
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB"
            )
    
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file not allowed"
        )
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create upload directory if it doesn't exist
    upload_dir = os.getenv("UPLOAD_DIR", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save encrypted file
    file_path = os.path.join(upload_dir, unique_filename)
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Generate encryption metadata
    if encryption_key:
        # Generate salt and derive key from password
        salt = os.urandom(16)
        derived_key, _ = encryption_manager.generate_key_from_password(encryption_key, salt)
        
        # Generate key hash for storage
        key_hash = encryption_manager.hash_key(derived_key)
        
        # Generate IV
        iv = os.urandom(16)
        iv_b64 = encryption_manager.encode_base64(iv)
        salt_b64 = encryption_manager.encode_base64(salt)
    else:
        # If no key provided, generate a random one (for demo purposes)
        salt = os.urandom(16)
        derived_key, _ = encryption_manager.generate_key_from_password("default-key", salt)
        key_hash = encryption_manager.hash_key(derived_key)
        iv_b64 = encryption_manager.encode_base64(os.urandom(16))
        salt_b64 = encryption_manager.encode_base64(salt)
    
    # Save file metadata to database
    video_file = VideoFile(
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        content_type=file.content_type,
        encryption_key_hash=key_hash,
        salt=salt_b64,
        iv=iv_b64,
        upload_date=datetime.utcnow(),
        processing_status="uploaded"
    )
    
    db.add(video_file)
    db.commit()
    db.refresh(video_file)
    
    # Send processing task to Kafka
    try:
        kafka_service.send_video_processing_task(
            video_file.id, 
            video_file.file_path, 
            video_file.filename
        )
    except Exception as e:
        # Log error but don't fail the upload
        print(f"Failed to send Kafka message: {e}")
    
    return {
        "message": "Video uploaded successfully",
        "file_id": video_file.id,
        "filename": video_file.filename,
        "original_filename": video_file.original_filename,
        "file_size": video_file.file_size,
        "upload_date": video_file.upload_date.isoformat(),
        "status": "encrypted_and_stored"
    } 
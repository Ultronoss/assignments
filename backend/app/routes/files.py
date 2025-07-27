from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import os
import aiofiles

from ..database import get_db
from ..models import VideoFile
from ..utils.encryption import encryption_manager

router = APIRouter()

@router.get("/files")
async def list_files(db: Session = Depends(get_db)):
    """List all uploaded video files"""
    files = db.query(VideoFile).order_by(VideoFile.upload_date.desc()).all()
    
    return [
        {
            "id": file.id,
            "original_filename": file.original_filename,
            "filename": file.filename,
            "file_size": file.file_size,
            "content_type": file.content_type,
            "upload_date": file.upload_date.isoformat(),
            "processing_status": file.processing_status,
            "is_processed": file.is_processed
        }
        for file in files
    ]

@router.get("/files/{file_id}")
async def get_file_info(file_id: int, db: Session = Depends(get_db)):
    """Get information about a specific file"""
    file = db.query(VideoFile).filter(VideoFile.id == file_id).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return {
        "id": file.id,
        "original_filename": file.original_filename,
        "filename": file.filename,
        "file_size": file.file_size,
        "content_type": file.content_type,
        "upload_date": file.upload_date.isoformat(),
        "processing_status": file.processing_status,
        "is_processed": file.is_processed,
        "encryption_key_hash": file.encryption_key_hash,
        "iv": file.iv
    }

class DecryptRequest(BaseModel):
    encryption_key: str

@router.post("/files/{file_id}/decrypt")
async def decrypt_and_download(
    file_id: int, 
    request: DecryptRequest,
    db: Session = Depends(get_db)
):
    """Decrypt and download a video file"""
    file = db.query(VideoFile).filter(VideoFile.id == file_id).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    if not os.path.exists(file.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    try:
        # Read encrypted file
        async with aiofiles.open(file.file_path, 'rb') as f:
            encrypted_data = await f.read()
        
        # Decode salt and IV from base64
        salt = encryption_manager.decode_base64(file.salt)
        iv = encryption_manager.decode_base64(file.iv)
        
        # Derive key from password using the stored salt
        derived_key, _ = encryption_manager.generate_key_from_password(request.encryption_key, salt)
        
        # Decrypt the data
        decrypted_data = encryption_manager.decrypt_data(
            encrypted_data, 
            derived_key, 
            iv
        )
        
        # Return decrypted file
        return Response(
            content=decrypted_data,
            media_type=file.content_type,
            headers={
                "Content-Disposition": f"attachment; filename={file.original_filename}"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to decrypt file: {str(e)}"
        )

@router.delete("/files/{file_id}")
async def delete_file(file_id: int, db: Session = Depends(get_db)):
    """Delete a video file"""
    file = db.query(VideoFile).filter(VideoFile.id == file_id).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Delete file from disk
    if os.path.exists(file.file_path):
        os.remove(file.file_path)
    
    # Delete from database
    db.delete(file)
    db.commit()
    
    return {"message": "File deleted successfully"} 
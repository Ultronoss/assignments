from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from .database import Base

class VideoFile(Base):
    __tablename__ = "video_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)
    encryption_key_hash = Column(String, nullable=False)  # Hash of the encryption key
    salt = Column(String, nullable=False)  # Salt for key derivation
    iv = Column(String, nullable=False)  # Initialization vector
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    is_processed = Column(Boolean, default=False)
    processing_status = Column(String, default="pending")
    
    def __repr__(self):
        return f"<VideoFile(id={self.id}, filename='{self.filename}', original_filename='{self.original_filename}')>" 
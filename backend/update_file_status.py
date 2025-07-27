#!/usr/bin/env python3
"""
Script to manually update file processing status for testing
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.models import VideoFile

def update_file_status():
    """Update all files to processed status"""
    db = SessionLocal()
    try:
        # Get all files
        files = db.query(VideoFile).all()
        print(f"Found {len(files)} files")
        
        for file in files:
            print(f"Updating file {file.id}: {file.original_filename}")
            file.processing_status = "processed"
            file.is_processed = True
        
        db.commit()
        print("All files updated to processed status")
        
        # Show updated files
        files = db.query(VideoFile).all()
        for file in files:
            print(f"File {file.id}: {file.original_filename} - Status: {file.processing_status}, Processed: {file.is_processed}")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_file_status() 
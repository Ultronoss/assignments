import json
import os
import logging
from kafka import KafkaConsumer
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import VideoFile

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.topic = "video-processing"
        self.consumer = None
        
    def start_processing(self):
        """Start consuming and processing video files"""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='video-processing-group'
            )
            
            logger.info(f"Started video processor, listening to topic: {self.topic}")
            
            for message in self.consumer:
                try:
                    self.process_video_file(message.value)
                except Exception as e:
                    logger.error(f"Error processing video file: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to start video processor: {e}")
        finally:
            if self.consumer:
                self.consumer.close()
    
    def process_video_file(self, message_data: dict):
        """Process a single video file"""
        file_id = message_data.get('file_id')
        file_path = message_data.get('file_path')
        filename = message_data.get('filename')
        
        logger.info(f"Processing video file: {filename} (ID: {file_id})")
        
        # Get database session
        db = SessionLocal()
        try:
            # Update status to processing
            video_file = db.query(VideoFile).filter(VideoFile.id == file_id).first()
            if not video_file:
                logger.error(f"Video file not found in database: {file_id}")
                return
            
            video_file.processing_status = "processing"
            db.commit()
            
            # Simulate video processing (in a real application, you might:
            # - Generate thumbnails
            # - Extract metadata
            # - Transcode to different formats
            # - Analyze content
            # - etc.)
            
            import time
            time.sleep(2)  # Simulate processing time
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"Video file not found on disk: {file_path}")
                video_file.processing_status = "failed"
                db.commit()
                return
            
            # Update status to processed
            video_file.processing_status = "processed"
            video_file.is_processed = True
            db.commit()
            
            logger.info(f"Successfully processed video file: {filename}")
            
        except Exception as e:
            logger.error(f"Error processing video file {file_id}: {e}")
            try:
                video_file.processing_status = "failed"
                db.commit()
            except:
                pass
        finally:
            db.close()

# Global video processor instance
video_processor = VideoProcessor() 
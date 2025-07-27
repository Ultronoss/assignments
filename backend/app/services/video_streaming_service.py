import json
import os
import logging
import asyncio
from typing import Dict, Any, Optional, AsyncGenerator
from kafka import KafkaConsumer, KafkaProducer
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import VideoFile
from ..utils.encryption import encryption_manager
import aiofiles
import tempfile
import shutil

logger = logging.getLogger(__name__)

class VideoStreamingService:
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        logger.info(f"Kafka bootstrap servers: {self.bootstrap_servers}")
        self.streaming_topic = "video-streaming"
        self.chunk_size = 1024 * 1024  # 1MB chunks
        self.temp_dir = tempfile.mkdtemp(prefix="video_streaming_")
        
    def get_producer(self):
        """Get Kafka producer for streaming responses"""
        try:
            return KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
        except Exception as e:
            logger.error(f"Failed to create Kafka producer: {e}")
            return None
    
    def get_consumer(self, topic: str, group_id: str):
        """Get Kafka consumer for streaming requests"""
        try:
            return KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id=group_id
            )
        except Exception as e:
            logger.error(f"Failed to create Kafka consumer: {e}")
            return None
    
    async def process_streaming_request(self, message_data: dict) -> bool:
        """Process a video streaming request"""
        file_id = message_data.get('file_id')
        encryption_key = message_data.get('encryption_key')
        request_id = message_data.get('request_id')
        
        logger.info(f"Processing streaming request for file {file_id}")
        
        # Get database session
        db = SessionLocal()
        try:
            # Get file info
            video_file = db.query(VideoFile).filter(VideoFile.id == file_id).first()
            if not video_file:
                logger.error(f"Video file not found: {file_id}")
                return False
            
            if not os.path.exists(video_file.file_path):
                logger.error(f"Video file not found on disk: {video_file.file_path}")
                return False
            
            # Decode salt and IV
            salt = encryption_manager.decode_base64(video_file.salt)
            iv = encryption_manager.decode_base64(video_file.iv)
            
            # Derive key from password
            derived_key, _ = encryption_manager.generate_key_from_password(encryption_key, salt)
            
            # Read and decrypt file in chunks
            producer = self.get_producer()
            if not producer:
                return False
            
            chunk_index = 0
            async with aiofiles.open(video_file.file_path, 'rb') as f:
                while True:
                    chunk = await f.read(self.chunk_size)
                    if not chunk:
                        break
                    
                    # Decrypt chunk
                    decrypted_chunk = encryption_manager.decrypt_data(chunk, derived_key, iv)
                    
                    # Send chunk via Kafka
                    chunk_message = {
                        "request_id": request_id,
                        "file_id": file_id,
                        "chunk_index": chunk_index,
                        "chunk_data": encryption_manager.encode_base64(decrypted_chunk),
                        "is_final": len(chunk) < self.chunk_size,
                        "content_type": video_file.content_type
                    }
                    
                    producer.send(
                        f"streaming-response-{request_id}",
                        value=chunk_message,
                        key=str(chunk_index)
                    )
                    
                    chunk_index += 1
                    await asyncio.sleep(0.01)  # Small delay to prevent overwhelming
            
            # Send completion message
            completion_message = {
                "request_id": request_id,
                "file_id": file_id,
                "status": "completed",
                "total_chunks": chunk_index
            }
            
            producer.send(
                f"streaming-response-{request_id}",
                value=completion_message,
                key="completion"
            )
            
            producer.flush()
            logger.info(f"Successfully streamed video file {file_id} in {chunk_index} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error streaming video file {file_id}: {e}")
            # Send error message
            producer = self.get_producer()
            if producer:
                error_message = {
                    "request_id": request_id,
                    "file_id": file_id,
                    "status": "error",
                    "error": str(e)
                }
                producer.send(f"streaming-response-{request_id}", value=error_message, key="error")
                producer.flush()
            return False
        finally:
            db.close()
    
    async def start_streaming_consumer(self):
        """Start consuming streaming requests"""
        consumer = self.get_consumer(self.streaming_topic, "video-streaming-group")
        if not consumer:
            return
        
        logger.info(f"Started video streaming consumer, listening to topic: {self.streaming_topic}")
        
        try:
            for message in consumer:
                try:
                    await self.process_streaming_request(message.value)
                except Exception as e:
                    logger.error(f"Error processing streaming request: {e}")
        except Exception as e:
            logger.error(f"Failed to start streaming consumer: {e}")
        finally:
            consumer.close()
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")

# Global streaming service instance
video_streaming_service = VideoStreamingService() 
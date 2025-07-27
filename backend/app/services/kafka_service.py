import json
import os
from kafka import KafkaProducer, KafkaConsumer
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class KafkaService:
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        logger.info(f"Kafka Service - Bootstrap servers: {self.bootstrap_servers}")
        self.producer = None
        self.consumer = None
        self.video_processing_topic = "video-processing"
        
    def get_producer(self):
        """Get or create Kafka producer"""
        if self.producer is None:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda k: k.encode('utf-8') if k else None
                )
            except Exception as e:
                logger.error(f"Failed to create Kafka producer: {e}")
                return None
        return self.producer
    
    def get_consumer(self, topic: str):
        """Get or create Kafka consumer"""
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='video-processing-group'
            )
            return consumer
        except Exception as e:
            logger.error(f"Failed to create Kafka consumer: {e}")
            return None
    
    def send_message(self, topic: str, message: Dict[str, Any], key: str = None):
        """Send message to Kafka topic"""
        producer = self.get_producer()
        if producer:
            try:
                future = producer.send(topic, value=message, key=key)
                future.get(timeout=10)  # Wait for message to be sent
                logger.info(f"Message sent to topic {topic}: {message}")
                return True
            except Exception as e:
                logger.error(f"Failed to send message to Kafka: {e}")
                return False
        return False
    
    def send_video_processing_task(self, file_id: int, file_path: str, filename: str):
        """Send video processing task to Kafka"""
        message = {
            "file_id": file_id,
            "file_path": file_path,
            "filename": filename,
            "task_type": "video_processing",
            "status": "pending"
        }
        return self.send_message(self.video_processing_topic, message, str(file_id))
    
    def close_producer(self):
        """Close Kafka producer"""
        if self.producer:
            self.producer.close()
            self.producer = None

# Global Kafka service instance
kafka_service = KafkaService() 
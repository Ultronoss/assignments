from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import json
import uuid
import asyncio
import logging

from ..database import get_db
from ..models import VideoFile
from ..services.kafka_service import kafka_service
from ..services.video_streaming_service import video_streaming_service

logger = logging.getLogger(__name__)
router = APIRouter()

class StreamingRequest(BaseModel):
    encryption_key: str

@router.post("/stream/{file_id}")
async def initiate_streaming(
    file_id: int,
    request: StreamingRequest,
    db: Session = Depends(get_db)
):
    """Initiate video streaming via Kafka"""
    # Check if file exists
    file = db.query(VideoFile).filter(VideoFile.id == file_id).first()
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    if not file.is_processed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not yet processed"
        )
    
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    
    # Send streaming request to Kafka
    streaming_message = {
        "file_id": file_id,
        "encryption_key": request.encryption_key,
        "request_id": request_id,
        "action": "start_streaming"
    }
    
    success = kafka_service.send_message(
        video_streaming_service.streaming_topic,
        streaming_message,
        str(file_id)
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate streaming"
        )
    
    return {
        "request_id": request_id,
        "file_id": file_id,
        "status": "streaming_initiated",
        "message": "Streaming request sent to Kafka"
    }

@router.get("/stream/{file_id}/status/{request_id}")
async def get_streaming_status(
    file_id: int,
    request_id: str,
    db: Session = Depends(get_db)
):
    """Get streaming status for a specific request"""
    # Check if file exists
    file = db.query(VideoFile).filter(VideoFile.id == file_id).first()
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return {
        "request_id": request_id,
        "file_id": file_id,
        "status": "active",
        "topic": f"streaming-response-{request_id}"
    }

class WebSocketManager:
    def __init__(self):
        self.active_connections: dict = {}
        self.kafka_consumers: dict = {}
    
    async def connect(self, websocket: WebSocket, request_id: str):
        await websocket.accept()
        self.active_connections[request_id] = websocket
        
        # Start Kafka consumer for this request
        await self.start_kafka_consumer(request_id)
    
    def disconnect(self, request_id: str):
        if request_id in self.active_connections:
            del self.active_connections[request_id]
        
        if request_id in self.kafka_consumers:
            self.kafka_consumers[request_id].close()
            del self.kafka_consumers[request_id]
    
    async def start_kafka_consumer(self, request_id: str):
        """Start Kafka consumer for streaming responses"""
        try:
            consumer = video_streaming_service.get_consumer(
                f"streaming-response-{request_id}",
                f"websocket-{request_id}"
            )
            
            if consumer:
                self.kafka_consumers[request_id] = consumer
                
                # Start consumer in background task
                asyncio.create_task(self.consume_messages(request_id, consumer))
        except Exception as e:
            logger.error(f"Failed to start Kafka consumer for {request_id}: {e}")
    
    async def consume_messages(self, request_id: str, consumer):
        """Consume messages from Kafka and send to WebSocket"""
        try:
            for message in consumer:
                if request_id in self.active_connections:
                    websocket = self.active_connections[request_id]
                    
                    # Send message to WebSocket
                    await websocket.send_text(json.dumps(message.value))
                    
                    # Check if streaming is complete
                    if message.value.get("status") in ["completed", "error"]:
                        await websocket.close()
                        self.disconnect(request_id)
                        break
        except Exception as e:
            logger.error(f"Error consuming messages for {request_id}: {e}")
        finally:
            self.disconnect(request_id)

# Global WebSocket manager
websocket_manager = WebSocketManager()

@router.websocket("/ws/stream/{request_id}")
async def websocket_streaming(websocket: WebSocket, request_id: str):
    """WebSocket endpoint for real-time video streaming"""
    await websocket_manager.connect(websocket, request_id)
    
    try:
        while True:
            # Keep connection alive and handle any client messages
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await websocket.send_text(json.dumps({"type": "heartbeat", "timestamp": data}))
    except WebSocketDisconnect:
        websocket_manager.disconnect(request_id)
    except Exception as e:
        logger.error(f"WebSocket error for {request_id}: {e}")
        websocket_manager.disconnect(request_id)

@router.get("/stream/{file_id}/chunks/{request_id}")
async def get_video_chunks(
    file_id: int,
    request_id: str,
    db: Session = Depends(get_db)
):
    """Get video chunks via HTTP streaming (alternative to WebSocket)"""
    # Check if file exists
    file = db.query(VideoFile).filter(VideoFile.id == file_id).first()
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    async def generate_chunks():
        """Generate video chunks from Kafka"""
        consumer = video_streaming_service.get_consumer(
            f"streaming-response-{request_id}",
            f"http-stream-{request_id}"
        )
        
        if not consumer:
            yield json.dumps({"error": "Failed to create Kafka consumer"})
            return
        
        try:
            for message in consumer:
                chunk_data = message.value
                
                # Send chunk as Server-Sent Events
                yield f"data: {json.dumps(chunk_data)}\n\n"
                
                # Check if streaming is complete
                if chunk_data.get("status") in ["completed", "error"]:
                    break
        except Exception as e:
            logger.error(f"Error streaming chunks for {request_id}: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            consumer.close()
    
    return StreamingResponse(
        generate_chunks(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    ) 
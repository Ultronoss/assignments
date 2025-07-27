# Video Streaming via Apache Kafka

This document describes the video streaming functionality that fetches and decrypts uploaded videos using Apache Kafka for smooth playback within the application.

## Overview

The video streaming system provides a complete flow from encrypted upload to successful decrypted playback via Kafka:

1. **Video Upload**: Videos are encrypted and stored securely
2. **Kafka Processing**: Videos are processed and made available for streaming
3. **Streaming Request**: Client requests video streaming with encryption key
4. **Kafka Streaming**: Video is decrypted and streamed in chunks via Kafka
5. **Video Playback**: Smooth playback in the web application

## Architecture

### Components

1. **Video Streaming Service** (`backend/app/services/video_streaming_service.py`)
   - Handles Kafka-based video streaming
   - Decrypts video chunks in real-time
   - Manages streaming sessions

2. **Streaming Routes** (`backend/app/routes/streaming.py`)
   - REST API endpoints for streaming
   - WebSocket support for real-time streaming
   - Server-Sent Events fallback

3. **Video Player Component** (`frontend/src/components/VideoPlayer.tsx`)
   - React component for video playback
   - Handles encryption key input
   - Supports WebSocket and EventSource streaming

4. **Streaming Processor** (`backend/streaming_processor.py`)
   - Standalone Kafka consumer for streaming requests
   - Runs as a separate service

### Kafka Topics

- `video-streaming`: Receives streaming requests
- `streaming-response-{request_id}`: Sends video chunks for specific requests

## Features

### 🔐 Secure Decryption
- Videos are decrypted on-demand using the provided encryption key
- AES-256-CBC encryption with PBKDF2 key derivation
- Salt and IV stored securely in database

### 📡 Real-time Streaming
- WebSocket-based streaming for low latency
- Server-Sent Events fallback for compatibility
- Chunked video delivery for smooth playback

### 🎥 Video Player
- Full-featured video player with controls
- Play/pause, volume, seek, fullscreen support
- Progress tracking and buffering indicators

### 🔄 Kafka Integration
- Asynchronous video processing
- Scalable streaming architecture
- Fault-tolerant message handling

## Usage

### Starting the Services

1. **Start all services with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **Verify services are running**:
   ```bash
   docker-compose ps
   ```

   You should see:
   - `postgres` - Database
   - `zookeeper` - Kafka coordination
   - `kafka` - Message broker
   - `backend` - FastAPI server
   - `frontend` - React application
   - `streaming-processor` - Kafka streaming consumer

### Using the Video Player

1. **Upload a video** through the web interface
2. **Wait for processing** (status will show "processed")
3. **Click the "Play" button** on any processed video
4. **Enter the encryption key** used during upload
5. **Enjoy smooth video playback** with full controls

### API Endpoints

#### Initiate Streaming
```http
POST /api/stream/{file_id}
Content-Type: application/json

{
  "encryption_key": "your_encryption_key"
}
```

Response:
```json
{
  "request_id": "uuid-string",
  "file_id": 123,
  "status": "streaming_initiated",
  "message": "Streaming request sent to Kafka"
}
```

#### WebSocket Streaming
```javascript
const ws = new WebSocket(`ws://localhost:8000/api/ws/stream/${requestId}`);
ws.onmessage = (event) => {
  const chunk = JSON.parse(event.data);
  // Handle video chunk
};
```

#### Server-Sent Events
```javascript
const eventSource = new EventSource(`/api/stream/${fileId}/chunks/${requestId}`);
eventSource.onmessage = (event) => {
  const chunk = JSON.parse(event.data);
  // Handle video chunk
};
```

## Technical Details

### Video Chunking
- Videos are streamed in 1MB chunks
- Each chunk is individually decrypted
- Chunks are reassembled in the browser using MediaSource API

### Encryption Flow
1. User provides encryption key
2. Key is derived using stored salt (PBKDF2)
3. Video chunks are decrypted using AES-256-CBC
4. Decrypted chunks are streamed to the player

### Error Handling
- Invalid encryption keys are handled gracefully
- Network errors trigger automatic retries
- Failed streams show user-friendly error messages

### Performance Optimizations
- Chunked streaming reduces memory usage
- WebSocket connections for low latency
- Background processing prevents UI blocking

## Troubleshooting

### Common Issues

1. **"Failed to initiate streaming"**
   - Check if Kafka is running: `docker-compose logs kafka`
   - Verify streaming processor is active: `docker-compose logs streaming-processor`

2. **"Video playback error"**
   - Ensure encryption key is correct
   - Check if video file exists and is processed
   - Verify WebSocket connection is established

3. **"Streaming connection failed"**
   - Check network connectivity
   - Verify Kafka topics are created
   - Restart streaming processor if needed

### Debug Commands

```bash
# Check Kafka topics
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Monitor Kafka messages
docker-compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic video-streaming --from-beginning

# Check streaming processor logs
docker-compose logs -f streaming-processor

# Check backend logs
docker-compose logs -f backend
```

## Security Considerations

- Encryption keys are never stored in plain text
- Video chunks are decrypted only when needed
- WebSocket connections are secured in production
- All API endpoints validate file access permissions

## Future Enhancements

- Adaptive bitrate streaming
- Video transcoding support
- Caching for frequently accessed videos
- Multi-user streaming sessions
- Mobile-optimized streaming 
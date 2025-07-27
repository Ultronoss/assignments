#!/usr/bin/env python3
"""
Video Streaming Processor
Handles Kafka-based video streaming requests
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.video_streaming_service import video_streaming_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to start the streaming processor"""
    logger.info("Starting Video Streaming Processor...")
    
    try:
        # Start the streaming consumer
        await video_streaming_service.start_streaming_consumer()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Error in streaming processor: {e}")
    finally:
        # Cleanup
        video_streaming_service.cleanup_temp_files()
        logger.info("Video Streaming Processor stopped")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 
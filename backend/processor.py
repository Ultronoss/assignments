#!/usr/bin/env python3
"""
Video Processor Service
Runs as a separate process to handle video processing tasks from Kafka
"""

import os
import sys
import time
import logging
from app.services.video_processor import video_processor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main function to run the video processor"""
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Video Processor Service...")
    
    # Wait for Kafka to be ready
    logger.info("Waiting for Kafka to be ready...")
    time.sleep(10)
    
    try:
        # Start processing
        video_processor.start_processing()
    except KeyboardInterrupt:
        logger.info("Video Processor Service stopped by user")
    except Exception as e:
        logger.error(f"Video Processor Service failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
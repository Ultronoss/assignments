#!/usr/bin/env python3
"""
Debug script to test Kafka connectivity
"""

import os
import sys
from kafka import KafkaProducer
import json

def test_kafka_connection():
    """Test Kafka connection and configuration"""
    print("Testing Kafka connection...")
    
    # Get environment variable
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    print(f"Bootstrap servers: {bootstrap_servers}")
    
    try:
        # Create producer
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        
        # Test sending a message
        message = {"test": "message"}
        future = producer.send("test-topic", value=message, key="test-key")
        result = future.get(timeout=10)
        print(f"Message sent successfully: {result}")
        
        producer.close()
        print("Kafka connection test successful!")
        
    except Exception as e:
        print(f"Kafka connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_kafka_connection() 
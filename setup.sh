#!/bin/bash

# Secure Video Upload Setup Script

echo "🚀 Setting up Secure Video Upload Application..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p backend/uploads
mkdir -p frontend/build

# Set proper permissions
chmod +x backend/processor.py

echo "🔧 Starting services with Docker Compose..."

# Start all services
sudo docker-compose up -d

echo "⏳ Waiting for services to start..."

# Wait for services to be ready
sleep 30

echo "🔍 Checking service status..."

# Check if services are running
if sudo docker-compose ps | grep -q "Up"; then
    echo "✅ All services are running!"
    echo ""
    echo "🌐 Application URLs:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   API Documentation: http://localhost:8000/docs"
    echo ""
    echo "📊 Service Status:"
    sudo docker-compose ps
    echo ""
    echo "📝 Next steps:"
    echo "   1. Open http://localhost:3000 in your browser"
    echo "   2. Enter an encryption key"
    echo "   3. Upload a video file"
    echo "   4. The file will be encrypted before upload"
    echo ""
    echo "🛑 To stop the application, run: sudo docker-compose down"
else
    echo "❌ Some services failed to start. Check the logs:"
    sudo docker-compose logs
    exit 1
fi 
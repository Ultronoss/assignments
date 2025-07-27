# Secure Video Upload with Encryption

A web application that allows users to upload video files with client-side encryption to ensure uploaded files are not directly playable by standard media players.

## Architecture

- **Backend**: FastAPI (Python)
- **Frontend**: React (TypeScript)
- **Database**: PostgreSQL
- **Message Queue**: Apache Kafka
- **Encryption**: AES-256-CBC

## Features

- Secure video file upload with encryption
- Client-side encryption before upload
- File metadata storage in PostgreSQL
- Asynchronous processing with Kafka
- Modern React UI with drag-and-drop upload
- File validation and progress tracking

## Project Structure

```
secure-video-upload/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── routes/         # API routes
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── requirements.txt
│   └── main.py
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   └── index.html
├── docker-compose.yml      # Docker setup
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites
- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Git**

### System Requirements
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: At least 10GB free space
- **OS**: Linux, macOS, or Windows with Docker support

### Quick Start (Recommended)

#### Option 1: Automated Setup
1. **Clone the repository:**
```bash
git clone <repository-url>
cd secure-video-upload
```

2. **Make the setup script executable:**
```bash
chmod +x setup.sh
```

3. **Run the automated setup:**
```bash
./setup.sh
```

#### Option 2: Manual Docker Setup
1. **Clone the repository:**
```bash
git clone <repository-url>
cd secure-video-upload
```

2. **Build and start all services:**
```bash
docker-compose up --build -d
```

3. **Wait for all services to start (2-3 minutes):**
```bash
docker-compose ps
```

### Access the Application
- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: PostgreSQL on localhost:5432

### First Time Setup Notes
- The first run may take 5-10 minutes to download Docker images and build containers
- All uploaded files are stored in Docker volumes and persist between restarts
- Database is automatically initialized on first run

### Troubleshooting

#### Common Issues:
1. **Port conflicts**: If ports 3000, 8000, or 5432 are in use, stop the conflicting services
2. **Docker permissions**: On Linux, you may need to add your user to the docker group:
   ```bash
   sudo usermod -aG docker $USER
   # Then log out and log back in
   ```
3. **Insufficient memory**: Ensure Docker has at least 4GB RAM allocated

#### Useful Commands:
```bash
# View logs
docker-compose logs -f

# Restart a specific service
docker-compose restart backend

# Stop all services
docker-compose down

# Clean up everything (including data)
docker-compose down -v
```

## Security Features

- Client-side AES-256-CBC encryption
- Encrypted file storage on server
- Secure key management
- File type validation
- Size limits and rate limiting

## 📖 Usage Guide

### How to Use the Application

1. **Upload a Video:**
   - Open http://localhost:3000 in your browser
   - Drag and drop a video file or click to select
   - Enter an encryption key (remember this key!)
   - Click "Upload Video"
   - Wait for the upload to complete

2. **Download a Video:**
   - In the file list, click "Download" next to any file
   - Enter the same encryption key used during upload
   - The file will be decrypted and downloaded

3. **Delete a File:**
   - Click "Delete" next to any file in the list
   - Confirm the deletion

### Testing the API

#### Upload a Video File:
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@your-video.mp4" \
  -F "encryption_key=your-secret-key"
```

#### List All Files:
```bash
curl -X GET http://localhost:8000/api/files
```

#### Download a File:
```bash
curl -X POST http://localhost:8000/api/files/{file_id}/decrypt \
  -H "Content-Type: application/json" \
  -d '{"encryption_key": "your-secret-key"}' \
  --output downloaded-video.mp4
```

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload` | Upload encrypted video file |
| `GET` | `/api/files` | List all uploaded files |
| `GET` | `/api/files/{file_id}` | Get file metadata |
| `POST` | `/api/files/{file_id}/decrypt` | Decrypt and download file |
| `DELETE` | `/api/files/{file_id}` | Delete a file |

## 🔒 Security Features

- **Client-side encryption**: Files are encrypted before upload using AES-256-CBC
- **Secure key derivation**: PBKDF2 with 100,000 iterations for key generation
- **Encrypted storage**: Files stored on server are encrypted and not directly playable
- **File validation**: MIME type and extension validation
- **Size limits**: Configurable maximum file size (default: 100MB)

## 📁 Project Structure

```
secure-video-upload/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models.py       # Database models
│   │   ├── routes/         # API routes
│   │   │   ├── upload.py   # Upload endpoint
│   │   │   └── files.py    # File management
│   │   ├── services/       # Business logic
│   │   │   ├── kafka_service.py
│   │   │   └── video_processor.py
│   │   └── utils/          # Utilities
│   │       └── encryption.py
│   ├── requirements.txt    # Python dependencies
│   ├── main.py            # FastAPI app entry point
│   └── Dockerfile         # Backend container
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── VideoUpload.tsx
│   │   │   └── FileList.tsx
│   │   ├── utils/          # Utilities
│   │   │   └── encryption.ts
│   │   └── types/          # TypeScript types
│   ├── package.json        # Node.js dependencies
│   └── Dockerfile          # Frontend container
├── docker-compose.yml      # Multi-service setup
├── setup.sh               # Automated setup script
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| **frontend** | 3000 | React application |
| **backend** | 8000 | FastAPI server |
| **postgres** | 5432 | PostgreSQL database |
| **kafka** | 9092 | Apache Kafka broker |
| **zookeeper** | 2181 | Kafka coordination |

## 📝 Development

### Local Development Setup
```bash
# Backend development
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend development
cd frontend
npm install
npm start
```

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker addresses
- `UPLOAD_DIR`: Directory for file uploads
- `MAX_FILE_SIZE`: Maximum file size in bytes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details 
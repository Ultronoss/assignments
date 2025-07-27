# Secure Video Upload - Usage Guide

## Overview

This application provides a secure way to upload video files with client-side encryption. The uploaded files are stored in an encrypted format on the server, making them unplayable by standard media players without the correct decryption key.

## Features

- **Client-side Encryption**: Videos are encrypted before upload using AES-256-CBC
- **Secure Storage**: Encrypted files are stored on the server
- **File Management**: List, download, and delete uploaded files
- **Asynchronous Processing**: Background processing using Apache Kafka
- **Modern UI**: React-based interface with drag-and-drop upload

## Quick Start

### Prerequisites

- Docker and Docker Compose
- At least 2GB of available RAM
- 1GB of available disk space

### Installation

1. **Clone or download the project**
   ```bash
   cd secure-video-upload
   ```

2. **Run the setup script**
   ```bash
   ./setup.sh
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

## How to Use

### Uploading a Video

1. **Open the application** in your browser at http://localhost:3000

2. **Enter an encryption key**
   - This key will be used to encrypt your video
   - Keep this key safe - you'll need it to download the file later
   - The key is never stored on the server

3. **Upload a video file**
   - Drag and drop a video file onto the upload area, or click to select
   - Supported formats: MP4, AVI, MOV, WMV, FLV, WebM, MKV, M4V
   - Maximum file size: 100MB

4. **Monitor the upload**
   - The progress bar shows upload status
   - The file will be encrypted before upload
   - Processing status will be updated in real-time

### Managing Files

#### Viewing Uploaded Files
- All uploaded files are listed on the main page
- Each file shows:
  - Original filename
  - File size
  - Upload date
  - Processing status

#### Downloading a File
1. Click the "Download" button next to the file
2. Enter the encryption key you used during upload
3. The file will be decrypted and downloaded to your computer

#### Deleting a File
1. Click the "Delete" button next to the file
2. Confirm the deletion
3. The file will be permanently removed from the server

## Security Features

### Encryption Details
- **Algorithm**: AES-256-CBC
- **Key Derivation**: PBKDF2 with 100,000 iterations
- **Client-side**: Encryption happens in the browser before upload
- **Server-side**: Only encrypted data is stored

### Security Measures
- Files are encrypted before leaving your browser
- Encryption keys are never transmitted to the server
- Server only stores encrypted files and metadata
- HTTPS encryption for all communications
- File type validation
- Size limits to prevent abuse

## API Endpoints

### Upload
- `POST /api/upload` - Upload an encrypted video file

### File Management
- `GET /api/files` - List all uploaded files
- `GET /api/files/{file_id}` - Get file information
- `POST /api/files/{file_id}/decrypt` - Decrypt and download file
- `DELETE /api/files/{file_id}` - Delete a file

## Architecture

### Services
- **Frontend**: React application (port 3000)
- **Backend**: FastAPI application (port 8000)
- **Database**: PostgreSQL (port 5432)
- **Message Queue**: Apache Kafka (port 9092)
- **Zookeeper**: Kafka coordination (port 2181)

### Data Flow
1. User selects video file and enters encryption key
2. File is encrypted in the browser using crypto-js
3. Encrypted file is uploaded to FastAPI backend
4. File metadata is stored in PostgreSQL
5. Processing task is sent to Kafka
6. Background processor handles file processing
7. User can download files by providing the encryption key

## Troubleshooting

### Common Issues

**Services won't start**
- Check if Docker and Docker Compose are installed
- Ensure ports 3000, 8000, 5432, 9092, 2181 are available
- Check Docker logs: `docker-compose logs`

**Upload fails**
- Verify file type is supported
- Check file size is under 100MB
- Ensure encryption key is provided
- Check browser console for errors

**Download fails**
- Verify the encryption key is correct
- Check if the file still exists on the server
- Ensure the file was processed successfully

**Database connection issues**
- Wait for PostgreSQL to fully start (may take 30-60 seconds)
- Check database logs: `docker-compose logs postgres`

### Logs and Debugging

**View all logs**
```bash
docker-compose logs
```

**View specific service logs**
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
docker-compose logs kafka
```

**Restart services**
```bash
docker-compose restart
```

**Stop all services**
```bash
docker-compose down
```

## Development

### Running Tests
```bash
python test_encryption.py
```

### Manual Setup (without Docker)
1. Install Python 3.9+ and Node.js 18+
2. Install PostgreSQL and Apache Kafka
3. Install backend dependencies: `pip install -r backend/requirements.txt`
4. Install frontend dependencies: `npm install` (in frontend directory)
5. Start backend: `uvicorn main:app --reload`
6. Start frontend: `npm start`

### Customization

**Changing file size limits**
- Edit `MAX_FILE_SIZE` in `backend/app/routes/upload.py`

**Adding new video formats**
- Update `ALLOWED_VIDEO_TYPES` in `backend/app/routes/upload.py`
- Update accept patterns in `frontend/src/components/VideoUpload.tsx`

**Modifying encryption settings**
- Edit encryption parameters in `backend/app/utils/encryption.py`
- Update client-side encryption in `frontend/src/utils/encryption.ts`

## Security Considerations

### Best Practices
- Use strong, unique encryption keys
- Don't share encryption keys
- Regularly backup important files
- Keep the application updated
- Monitor for suspicious activity

### Limitations
- Encryption keys cannot be recovered if lost
- No built-in key management system
- Files are stored on the local server
- No automatic backup system

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Test the encryption functionality
4. Verify all services are running correctly

## License

This project is provided as-is for educational and demonstration purposes. 
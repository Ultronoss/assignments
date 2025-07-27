# 🤝 Contributing to Secure Video Upload

Thank you for your interest in contributing to the Secure Video Upload project! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Git
- Basic knowledge of Python, React, and Docker

### Fork and Clone
1. Fork the repository on GitHub
2. Clone your fork locally:
```bash
git clone https://github.com/your-username/secure-video-upload.git
cd secure-video-upload
```

## 🔧 Development Setup

### Quick Development Start
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Local Development (Without Docker)

#### Backend Development
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://video_user:secure_password@localhost:5432/secure_video_db"
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"

# Run the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 📝 Code Style

### Python (Backend)
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for function parameters and return values
- Maximum line length: 88 characters (Black formatter)
- Use f-strings for string formatting
- Add docstrings for all public functions and classes

Example:
```python
from typing import List, Optional
from fastapi import HTTPException, status

def get_file_by_id(file_id: int, db: Session) -> Optional[VideoFile]:
    """
    Retrieve a video file by its ID.
    
    Args:
        file_id: The unique identifier of the file
        db: Database session
        
    Returns:
        VideoFile object if found, None otherwise
        
    Raises:
        HTTPException: If file is not found
    """
    file = db.query(VideoFile).filter(VideoFile.id == file_id).first()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return file
```

### TypeScript/React (Frontend)
- Use TypeScript for all new code
- Follow ESLint and Prettier configurations
- Use functional components with hooks
- Implement proper error handling
- Add JSDoc comments for complex functions

Example:
```typescript
interface FileUploadProps {
  onUploadSuccess: (file: FileInfo) => void;
  onUploadError: (error: string) => void;
}

/**
 * Handles file upload with encryption
 * @param file - The file to upload
 * @param encryptionKey - The encryption key
 */
const handleFileUpload = async (
  file: File, 
  encryptionKey: string
): Promise<void> => {
  try {
    const encryptedFile = await encryptFile(file, encryptionKey);
    // Upload logic...
  } catch (error) {
    console.error('Upload failed:', error);
    throw new Error('Failed to upload file');
  }
};
```

## 🧪 Testing

### Backend Testing
```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Frontend Testing
```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

### Integration Testing
```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
pytest tests/integration/

# Cleanup
docker-compose -f docker-compose.test.yml down
```

## 🔄 Pull Request Process

### Before Submitting a PR

1. **Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes:**
   - Write clear, descriptive commit messages
   - Follow the code style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes:**
   - Run all tests locally
   - Test the application manually
   - Ensure no linting errors

4. **Commit your changes:**
```bash
git add .
git commit -m "feat: add new encryption feature"
git push origin feature/your-feature-name
```

### PR Guidelines

- **Title**: Use conventional commit format (e.g., "feat: add file encryption")
- **Description**: Clearly describe what the PR does and why
- **Tests**: Include tests for new functionality
- **Documentation**: Update README or other docs if needed
- **Screenshots**: Include screenshots for UI changes

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

## 🐛 Reporting Issues

### Bug Reports
When reporting bugs, please include:

1. **Environment:**
   - OS and version
   - Docker version
   - Browser (for frontend issues)

2. **Steps to reproduce:**
   - Clear, step-by-step instructions
   - Expected vs actual behavior

3. **Additional information:**
   - Error messages/logs
   - Screenshots if applicable
   - Console output

### Feature Requests
For feature requests:

1. **Describe the feature** in detail
2. **Explain the use case** and benefits
3. **Provide examples** of how it would work
4. **Consider implementation** complexity

## 📚 Documentation

### Adding Documentation
- Update README.md for user-facing changes
- Add inline comments for complex code
- Create new documentation files for major features
- Keep API documentation up to date

### Documentation Standards
- Use clear, concise language
- Include code examples
- Add screenshots for UI changes
- Follow existing formatting patterns

## 🔒 Security

### Security Guidelines
- Never commit sensitive information (passwords, API keys)
- Use environment variables for configuration
- Validate all user inputs
- Follow security best practices
- Report security vulnerabilities privately

### Security Reporting
If you find a security vulnerability:

1. **DO NOT** create a public issue
2. Email the maintainers privately
3. Provide detailed information about the vulnerability
4. Allow time for assessment and fix

## 🏷️ Release Process

### Versioning
We follow [Semantic Versioning](https://semver.org/):
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version bumped
- [ ] Release notes written

## 📞 Getting Help

### Communication Channels
- **Issues**: Use GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers for security issues

### Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

## 🙏 Acknowledgments

Thank you for contributing to the Secure Video Upload project! Your contributions help make the application better for everyone.

---

**Note**: This contributing guide is a living document. Feel free to suggest improvements or clarifications through issues or pull requests. 
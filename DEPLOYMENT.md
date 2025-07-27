# 🚀 Deployment Guide

This guide covers different deployment scenarios for the Secure Video Upload application.

## 📋 Prerequisites

- Docker and Docker Compose installed
- Git
- At least 4GB RAM available
- 10GB+ free disk space

## 🏠 Local Development Deployment

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd secure-video-upload

# Run the application
./setup.sh

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## ☁️ Production Deployment

### Option 1: Docker Compose on VPS/Cloud Server

#### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

#### 2. Application Deployment
```bash
# Clone repository
git clone <repository-url>
cd secure-video-upload

# Create production environment file
cat > .env << EOF
DATABASE_URL=postgresql://video_user:secure_password@postgres:5432/secure_video_db
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=104857600
NODE_ENV=production
EOF

# Start the application
docker-compose up -d

# Check status
docker-compose ps
```

#### 3. Reverse Proxy Setup (Nginx)
```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/secure-video-upload << EOF
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/secure-video-upload /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 2: Kubernetes Deployment

#### 1. Create Kubernetes Manifests

**namespace.yaml:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: secure-video-upload
```

**postgres-deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: secure-video-upload
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: "secure_video_db"
        - name: POSTGRES_USER
          value: "video_user"
        - name: POSTGRES_PASSWORD
          value: "secure_password"
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: secure-video-upload
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: secure-video-upload
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

**backend-deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: secure-video-upload
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/secure-video-backend:latest
        env:
        - name: DATABASE_URL
          value: "postgresql://video_user:secure_password@postgres:5432/secure_video_db"
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "kafka:9092"
        ports:
        - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: secure-video-upload
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
```

**frontend-deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: secure-video-upload
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/secure-video-frontend:latest
        ports:
        - containerPort: 3000
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: secure-video-upload
spec:
  selector:
    app: frontend
  ports:
  - port: 3000
    targetPort: 3000
```

#### 2. Deploy to Kubernetes
```bash
# Apply manifests
kubectl apply -f namespace.yaml
kubectl apply -f postgres-deployment.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml

# Check deployment status
kubectl get pods -n secure-video-upload
```

## 🔧 Environment Configuration

### Production Environment Variables

Create a `.env` file for production:

```bash
# Database
DATABASE_URL=postgresql://video_user:secure_password@postgres:5432/secure_video_db

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# File Upload
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=104857600

# Security
SECRET_KEY=your-super-secret-key-here
ENCRYPTION_KEY=your-encryption-key

# Frontend
REACT_APP_API_URL=https://your-domain.com/api

# Logging
LOG_LEVEL=INFO
```

## 🔒 Security Considerations

### Production Security Checklist

- [ ] Change default database passwords
- [ ] Use HTTPS with valid SSL certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Regular security updates
- [ ] Backup strategy implementation
- [ ] Rate limiting configuration
- [ ] Input validation and sanitization

### SSL/TLS Setup

```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring and Logging

### Health Checks
```bash
# Check application health
curl http://localhost:8000/health

# Check database connection
docker-compose exec postgres pg_isready -U video_user -d secure_video_db

# Monitor logs
docker-compose logs -f
```

### Backup Strategy
```bash
# Database backup
docker-compose exec postgres pg_dump -U video_user secure_video_db > backup.sql

# File backup
tar -czf uploads-backup.tar.gz uploads/

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U video_user secure_video_db > backup_$DATE.sql
tar -czf uploads-backup_$DATE.tar.gz uploads/
```

## 🚨 Troubleshooting

### Common Issues

1. **Port conflicts**: Check if ports 3000, 8000, 5432 are available
2. **Memory issues**: Ensure sufficient RAM (4GB+)
3. **Disk space**: Monitor available storage
4. **Network issues**: Check firewall and DNS settings

### Debug Commands
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs [service-name]

# Access container shell
docker-compose exec [service-name] bash

# Check resource usage
docker stats
```

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale backend services
docker-compose up -d --scale backend=3 --scale frontend=2

# Load balancer configuration
# Use Nginx or HAProxy for load balancing
```

### Performance Optimization
- Enable database connection pooling
- Configure Redis for caching
- Use CDN for static assets
- Implement file compression
- Optimize Docker images

## 📞 Support

For deployment issues:
1. Check the troubleshooting section
2. Review application logs
3. Verify system requirements
4. Consult the main README.md 
# Docker Setup Guide

## Prerequisites

- Docker and Docker Compose installed
- At least 4GB of available RAM
- 10GB of available disk space

## Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd ucuenca-chatbot
   ```

2. **Set up environment variables:**
   ```bash
   cp env.example .env
   ```
   Edit `.env` file with your actual API keys and configuration.

3. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Database: localhost:5433

## Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
DB_NAME=ucuenca_chatbot

# API Keys (Required)
DEEPSEEK_API_KEY=your_deepseek_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256

# Application Settings
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=*
```

## Docker Compose Services

### App Service
- **Port:** 8000
- **Health Check:** http://localhost:8000/health
- **Dependencies:** PostgreSQL database
- **Volumes:** 
  - `./resources:/app/resources` (PDF files)
  - `./sources.db:/app/sources.db` (FAISS index)

### Database Service
- **Image:** postgres:15-alpine
- **Port:** 5433 (external), 5432 (internal)
- **Health Check:** PostgreSQL readiness
- **Volume:** `postgres_data` (persistent data)

## Useful Commands

### Development
```bash
# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build
```

### Database Operations
```bash
# Access database
docker-compose exec db psql -U postgres -d ucuenca_chatbot

# Run migrations
docker-compose exec app alembic upgrade head

# Reset database
docker-compose down -v
docker-compose up --build
```

### Troubleshooting

#### Common Issues

1. **Port already in use:**
   ```bash
   # Check what's using the port
   netstat -tulpn | grep :8000
   # Or change ports in docker-compose.yml
   ```

2. **Database connection issues:**
   ```bash
   # Check database logs
   docker-compose logs db
   
   # Restart database
   docker-compose restart db
   ```

3. **Memory issues:**
   ```bash
   # Check container resource usage
   docker stats
   
   # Increase Docker memory limit in Docker Desktop settings
   ```

4. **Build failures:**
   ```bash
   # Clear Docker cache
   docker system prune -a
   
   # Rebuild without cache
   docker-compose build --no-cache
   ```

#### Health Check Failures

- **App health check failing:** Check if the application is starting properly
- **Database health check failing:** Check if PostgreSQL is initializing correctly

#### Performance Optimization

1. **Increase Docker resources:**
   - Memory: 4GB minimum, 8GB recommended
   - CPU: 2 cores minimum, 4 cores recommended

2. **Use Docker volumes for development:**
   ```yaml
   volumes:
     - .:/app
     - /app/venv
   ```

## Production Deployment

For production, consider:

1. **Use proper secrets management**
2. **Set up proper logging**
3. **Configure backup strategies**
4. **Use reverse proxy (nginx)**
5. **Set up monitoring and alerting**

## Security Considerations

1. **Change default passwords**
2. **Use strong SECRET_KEY**
3. **Limit CORS_ORIGINS in production**
4. **Regular security updates**
5. **Network isolation**

## Monitoring

```bash
# Check service status
docker-compose ps

# Monitor resource usage
docker stats

# View service logs
docker-compose logs [service_name]
``` 
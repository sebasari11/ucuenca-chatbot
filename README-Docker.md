# Docker Deployment Guide

This guide explains how to deploy the UCUENCA Chatbot using Docker and Docker Compose.

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system
- Git (to clone the repository)

## Quick Start

1. **Clone the repository and navigate to the project directory:**
   ```bash
   cd ucuenca-chatbot
   ```

2. **Create environment file:**
   ```bash
   cp env.example .env
   ```

3. **Edit the `.env` file with your configuration:**
   ```bash
   nano .env
   ```
   
   Make sure to set:
   - `DB_PASSWORD`: A secure password for PostgreSQL
   - `SECRET_KEY`: A secure secret key for JWT tokens
   - `DEEPSEEK_API_KEY`: Your DeepSeek API key
   - `GEMINI_API_KEY`: Your Gemini API key

4. **Build and start the services:**
   ```bash
   docker-compose up -d
   ```

5. **Check if services are running:**
   ```bash
   docker-compose ps
   ```

6. **View logs:**
   ```bash
   docker-compose logs -f app
   ```

## Accessing the Application

- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Database:** localhost:5432 (PostgreSQL)

## Database Migrations

If you need to run database migrations:

```bash
docker-compose exec app alembic upgrade head
```

## Stopping the Services

```bash
docker-compose down
```

To also remove volumes (this will delete all data):
```bash
docker-compose down -v
```

## Production Deployment

For production deployment, consider:

1. **Using a reverse proxy (nginx):**
   ```yaml
   # Add to docker-compose.yml
   nginx:
     image: nginx:alpine
     ports:
       - "80:80"
       - "443:443"
     volumes:
       - ./nginx.conf:/etc/nginx/nginx.conf
     depends_on:
       - app
   ```

2. **Setting up SSL certificates**

3. **Using environment-specific configurations**

4. **Setting up monitoring and logging**

## Troubleshooting

### Common Issues

1. **Port already in use:**
   - Change the port mapping in `docker-compose.yml`
   - Example: `"8001:8000"` instead of `"8000:8000"`

2. **Database connection issues:**
   - Ensure the database service is running: `docker-compose ps`
   - Check database logs: `docker-compose logs db`

3. **Permission issues:**
   - Ensure the `resources` directory has proper permissions
   - The Dockerfile creates a non-root user for security

### Viewing Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs app
docker-compose logs db

# Follow logs in real-time
docker-compose logs -f app
```

### Accessing the Container

```bash
# Access the app container
docker-compose exec app bash

# Access the database
docker-compose exec db psql -U postgres -d ucuenca_chatbot
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_USER` | PostgreSQL username | postgres |
| `DB_PASSWORD` | PostgreSQL password | postgres |
| `DB_HOST` | Database host | localhost |
| `DB_NAME` | Database name | ucuenca_chatbot |
| `DB_PORT` | Database port | 5432 |
| `DEEPSEEK_API_KEY` | DeepSeek API key | None |
| `GEMINI_API_KEY` | Gemini API key | None |
| `SECRET_KEY` | JWT secret key | None |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ENVIRONMENT` | Environment mode | production |
| `DEBUG` | Debug mode | false |
| `CORS_ORIGINS` | CORS origins | * | 
# Docker Deployment Guide

This guide explains how to deploy the Dynamic Interactive Decentralized Privacy Policy System using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10 or later)
- Docker Compose (version 2.0 or later)
- OpenAI API key

## Quick Start

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd Dynamic-Interactive-Decentralized-Privacy-Policy-System
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_openai_api_key_here
   ```

3. **Build and start the services**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Architecture

The application consists of two main services:

- **Backend**: FastAPI application running on port 8000
- **Frontend**: Next.js application running on port 3000

## Docker Commands

### Start services in detached mode
```bash
docker-compose up -d
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop services
```bash
docker-compose down
```

### Rebuild services
```bash
docker-compose up --build
```

### Force rebuild without cache
```bash
docker-compose build --no-cache
```

## Environment Variables

### Required
- `OPENAI_API_KEY`: Your OpenAI API key

### Optional
- `OPENAI_MODEL_PRIMARY`: Primary model (default: gpt-4o)
- `OPENAI_MODEL_SECONDARY`: Secondary model (default: gpt-4o-mini)
- `LITELLM_PROXY_URL`: LiteLLM proxy URL if using one
- `DEBUG`: Enable debug mode (default: false in production)

## Development vs Production

### Development
For development with hot reload:
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Production
Use Docker Compose for production deployment:
```bash
docker-compose up -d
```

## Troubleshooting

### Health Checks
Both services include health checks. Check status with:
```bash
docker-compose ps
```

### Container Logs
If services fail to start, check logs:
```bash
docker-compose logs backend
docker-compose logs frontend
```

### Common Issues

1. **Backend fails with OpenAI error**: Ensure `OPENAI_API_KEY` is set correctly in `.env`
2. **Frontend can't connect to backend**: Check that backend is healthy and ports are not blocked
3. **Permission errors**: Ensure Docker has proper permissions on your system

### Ports
- Backend: 8000
- Frontend: 3000

Make sure these ports are available on your host system.

## Data Persistence

Generated webpages are persisted in a Docker volume mapped to `./backend/generated_webpages`.

## Monitoring

Health check endpoints:
- Backend: http://localhost:8000/health
- Frontend: http://localhost:3000 (main page serves as health check)

## Scaling

To scale services (e.g., multiple frontend instances):
```bash
docker-compose up --scale frontend=3 -d
```

Note: You'll need a load balancer for multiple frontend instances. 
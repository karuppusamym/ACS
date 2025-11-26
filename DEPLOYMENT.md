# Production Deployment Guide

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- PostgreSQL with pgvector extension (included in docker-compose)

### 1. Environment Setup

**Backend (.env)**:
```bash
cd backend
cp .env.example .env
# Edit .env with your actual values:
# - Change SECRET_KEY to a secure random string
# - Add your OpenAI API key
# - Update database credentials if needed
```

**Frontend**:
```bash
# No .env needed for Docker deployment
# API URL is configured in docker-compose.yml
```

### 2. Build and Run

```bash
# From project root
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (WARNING: deletes database)
docker-compose down -v
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs (dev only)
- **Database**: localhost:5432

### 4. Database Migrations

```bash
# Run migrations (when Alembic is set up)
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

## Manual Deployment (Without Docker)

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your values

# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Start production server
npm start
```

## Production Checklist

### Security
- [ ] Change `SECRET_KEY` in backend .env
- [ ] Add real API keys (OpenAI, etc.)
- [ ] Update `CORS_ORIGINS` to your production domain
- [ ] Enable HTTPS (use reverse proxy like Nginx)
- [ ] Set up firewall rules
- [ ] Enable rate limiting

### Database
- [ ] Set strong database password
- [ ] Enable database backups
- [ ] Set up connection pooling
- [ ] Configure database monitoring

### Monitoring
- [ ] Set up log aggregation (ELK, CloudWatch, etc.)
- [ ] Configure error tracking (Sentry)
- [ ] Set up uptime monitoring
- [ ] Configure alerts for critical errors

### Performance
- [ ] Enable caching (Redis)
- [ ] Configure CDN for frontend assets
- [ ] Optimize database queries
- [ ] Set up load balancing (if needed)

## Environment Variables

### Backend Required
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key (generate with `openssl rand -hex 32`)
- `OPENAI_API_KEY` - OpenAI API key (optional for demo mode)

### Backend Optional
- `CORS_ORIGINS` - Comma-separated list of allowed origins
- `ENVIRONMENT` - development/staging/production
- `LOG_LEVEL` - DEBUG/INFO/WARNING/ERROR

### Frontend
- `NEXT_PUBLIC_API_URL` - Backend API URL

## Troubleshooting

### Backend won't start
- Check database connection
- Verify .env file exists and has correct values
- Check logs: `docker-compose logs backend`

### Frontend can't connect to backend
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS settings in backend
- Ensure backend is running

### Database connection errors
- Verify PostgreSQL is running
- Check database credentials
- Ensure pgvector extension is installed

## Scaling

### Horizontal Scaling
- Use load balancer (Nginx, HAProxy)
- Run multiple backend instances
- Use shared database and Redis

### Vertical Scaling
- Increase container resources in docker-compose
- Optimize database queries
- Enable caching

## Backup and Restore

### Database Backup
```bash
docker-compose exec postgres pg_dump -U postgres agentic_analyst > backup.sql
```

### Database Restore
```bash
docker-compose exec -T postgres psql -U postgres agentic_analyst < backup.sql
```

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review environment variables
3. Verify all services are running: `docker-compose ps`

# Quick PostgreSQL Setup with Docker

## Option 1: Using Docker Compose (Recommended - Easiest)

### Step 1: Create Backend .env File
```bash
cd backend
copy .env.example .env
```

### Step 2: Edit .env File
Open `backend/.env` and set:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/agentic_analyst
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=agentic_analyst
SECRET_KEY=your-secret-key-change-this-to-something-random
OPENAI_API_KEY=your-openai-api-key-here
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Step 3: Start PostgreSQL with Docker Compose
```bash
# From project root
docker-compose up -d postgres
```

This will:
- Download PostgreSQL with pgvector
- Start it on port 5432
- Create database `agentic_analyst`
- Keep data persistent in a Docker volume

### Step 4: Verify PostgreSQL is Running
```bash
docker-compose ps
```

You should see `postgres` with status "Up"

### Step 5: Create Database Tables
We need to create the tables. For now, we'll use a simple Python script:

```bash
cd backend
python -c "from app.db.base import Base; from app.db.session import engine; from app.models.models import *; Base.metadata.create_all(bind=engine)"
```

### Step 6: Restart Backend
Stop the current backend (Ctrl+C) and restart:
```bash
python main.py
```

---

## Option 2: PostgreSQL Only (Without Full Docker Compose)

If you want just PostgreSQL without the full stack:

```bash
docker run -d \
  --name agentic_postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=agentic_analyst \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

Then follow steps 2, 5, and 6 from Option 1.

---

## Option 3: Full Stack with Docker Compose

To run everything (PostgreSQL + Backend + Frontend) in Docker:

### Step 1: Stop Current Servers
- Stop `npm run dev` (Ctrl+C)
- Stop `python main.py` (Ctrl+C)

### Step 2: Build and Start All Services
```bash
# From project root
docker-compose up --build
```

This will start:
- PostgreSQL on port 5432
- Backend on port 8000
- Frontend on port 3000

Access at: http://localhost:3000

---

## Troubleshooting

### Port 5432 Already in Use
```bash
# Stop any existing PostgreSQL
docker stop agentic_postgres
docker rm agentic_postgres

# Or if using docker-compose
docker-compose down
```

### Check PostgreSQL Logs
```bash
docker-compose logs postgres
```

### Connect to PostgreSQL
```bash
docker exec -it thermal-filament-postgres-1 psql -U postgres -d agentic_analyst
```

### Reset Database
```bash
docker-compose down -v  # WARNING: Deletes all data
docker-compose up -d postgres
```

---

## Quick Commands Reference

```bash
# Start only PostgreSQL
docker-compose up -d postgres

# Stop PostgreSQL
docker-compose stop postgres

# View logs
docker-compose logs -f postgres

# Check status
docker-compose ps

# Remove everything (including data)
docker-compose down -v
```

---

## What's Next?

After PostgreSQL is running:
1. ✅ Backend will connect automatically
2. ✅ Tables will be created
3. ✅ You can start using the app!

Test it:
1. Go to http://localhost:3000
2. Try to create a user (will test DB connection)
3. Create a model
4. Start chatting!

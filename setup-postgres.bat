@echo off
echo ========================================
echo PostgreSQL Setup for Agentic Data Analyst
echo ========================================
echo.

echo Step 1: Creating .env file...
cd backend
if not exist .env (
    copy .env.example .env
    echo .env file created! Please edit it with your OpenAI API key.
) else (
    echo .env file already exists.
)
cd ..

echo.
echo Step 2: Starting PostgreSQL with Docker...
docker-compose up -d postgres

echo.
echo Step 3: Waiting for PostgreSQL to be ready...
timeout /t 5 /nobreak > nul

echo.
echo Step 4: Creating database tables...
cd backend
python -c "from app.db.base import Base; from app.db.session import engine; from app.models.models import *; Base.metadata.create_all(bind=engine)"
cd ..

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo PostgreSQL is running on localhost:5432
echo Database: agentic_analyst
echo Username: postgres
echo Password: password
echo.
echo Next steps:
echo 1. Edit backend/.env and add your OPENAI_API_KEY
echo 2. Restart your backend: cd backend ^&^& python main.py
echo 3. Open http://localhost:3000 in your browser
echo.
pause

# Agentic Data Analysis Platform

A premium, AI-powered data analysis platform with natural language querying, semantic modeling, and process mining capabilities.

## 🚀 Features

- **AI-Powered Analysis**: Chat with your data using natural language
- **Multi-Database Support**: PostgreSQL, MySQL, MS SQL, Oracle, Snowflake, BigQuery
- **Semantic Layer**: Add business context to your data models
- **Process Mining**: Discover and analyze business processes from event logs
- **LLM Flexibility**: Support for OpenAI, Anthropic, Google Gemini, and Azure OpenAI
- **Production Ready**: Docker containerization, structured logging, error handling

## 📋 Prerequisites

- Docker and Docker Compose (recommended)
- OR Node.js 20+ and Python 3.11+ (for manual setup)

## 🏃 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/karuppusamym/ACS.git
cd ACS

# 2. Set up environment variables
cd backend
cp .env.example .env
# Edit .env with your API keys and secrets

cd ../frontend
cp .env.example .env.local
# Edit .env.local with NEXT_PUBLIC_API_URL=http://localhost:8000

# 3. Start all services
cd ..
docker-compose up -d

# 4. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### Option 2: Manual Setup

**Backend**:
```bash
cd backend
python -m venv .venv
# Windows:
.\.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
python main.py
```

**Frontend**:
```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT.md) - Production deployment instructions
- [Production Plan](production_plan.md) - Production readiness checklist
- [API Documentation](http://localhost:8000/api/docs) - Interactive API docs (when running)

## 🏗️ Architecture

### Tech Stack

**Frontend**:
- Next.js 14 with App Router
- TypeScript
- TailwindCSS v3
- Shadcn/UI components

**Backend**:
- Python 3.11
- FastAPI
- SQLAlchemy ORM
- PostgreSQL with pgvector
- LangChain & LangGraph
- PM4Py for process mining

### Project Structure

```
ACS/
├── frontend/                 # Next.js application
│   ├── app/                 # App router pages
│   ├── components/          # React components
│   └── lib/                 # Utilities
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core functionality
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── agent/          # AI agent logic
│   └── main.py             # Application entry point
└── docker-compose.yml      # Docker orchestration
```

## 🔐 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Rate limiting (configurable)
- Security headers (HSTS, CSP, etc.)
- Environment-based secrets management

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📊 Monitoring

- Structured logging with Loguru
- Health check endpoint: `/health`
- Request timing headers
- Error tracking ready (Sentry integration available)

## 🔧 Configuration

### Environment Variables

**Backend** (`.env`):
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/db
SECRET_KEY=your-secret-key
OPENAI_API_KEY=sk-...
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Frontend**:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🚢 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions including:
- Docker deployment
- Manual deployment
- Production checklist
- Scaling strategies
- Backup and restore

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

[Your License Here]

## 🆘 Support

For issues or questions:
1. Check the [Deployment Guide](DEPLOYMENT.md)
2. Review logs: `docker-compose logs`
3. Open an issue on GitHub

## 🎯 Roadmap

- [ ] Advanced workflow builder with drag-and-drop
- [ ] Real-time collaboration features
- [ ] Advanced process mining (conformance checking, simulation)
- [ ] Multi-tenant support
- [ ] Mobile app

---

Built with ❤️ using Next.js and FastAPI

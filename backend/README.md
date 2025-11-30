# TrendPulse Backend (FastAPI)

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (running)
- Redis 7+ (running)

### Setup

1. **Copy environment file:**
```bash
cp ../.env.example ../.env
# Edit .env with your database credentials
```

2. **Install dependencies:**
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

3. **Setup database:**
```bash
# Generate initial migration
alembic revision --autogenerate -m "initial_auth_tables"

# Apply migration
alembic upgrade head
```

4. **Run server:**
```bash
uvicorn app.main:app --reload --port 8000
```

Server will be available at: http://localhost:8000

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── alembic/              # Database migrations
│   ├── versions/         # Migration files
│   └── env.py           # Alembic config
├── app/
│   ├── api/             # API routes
│   ├── core/            # Config, database, security
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── main.py          # FastAPI app
├── tests/               # Test files
├── alembic.ini          # Alembic configuration
└── requirements.txt     # Python dependencies
```

## Environment Variables

Key variables in `.env`:

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/trendpulse
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

See `../.env.example` for all variables.

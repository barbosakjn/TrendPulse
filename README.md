# TrendPulse

**Trend Discovery Platform for SaaS & Digital Products**

TrendPulse is an intelligent trend discovery platform designed to identify emerging opportunities in the digital marketplace. It aggregates data from multiple sources including Google Trends, YouTube, and Reddit to provide actionable insights for entrepreneurs, content creators, and digital product developers.

---

## Features

- **Unified Dashboard**: Single view aggregating multiple trend sources
- **Opportunity Scoring**: Proprietary algorithm rating trend potential (0-100)
- **Advanced Filtering**: Search by niche, region, language, time range, and data source
- **Real-time Alerts**: Notifications when relevant trends emerge
- **Favorites System**: Save and organize trends with personal notes
- **Historical Tracking**: Monitor trend evolution over time
- **Multi-language**: English, Portuguese (BR), and Spanish support
- **Export Options**: CSV, JSON, PDF, XLSX formats

---

## Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety and better DX
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Accessible component library
- **TanStack Query** - Data fetching and caching
- **Zustand** - State management
- **Recharts** - Data visualizations
- **next-intl** - Internationalization

### Backend
- **FastAPI** - High-performance Python API framework
- **SQLAlchemy 2.0** - Database ORM
- **Pydantic v2** - Data validation
- **Celery** - Async task queue for data collection
- **Redis** - Caching and message broker
- **PostgreSQL 15** - Primary database

### Data Sources
- **Pytrends** - Google Trends integration
- **YouTube Data API v3** - Trending videos
- **Reddit API (PRAW)** - Hot topics and discussions

---

## Project Structure

```
trendpulse/
├── frontend/                    # Next.js frontend application
│   ├── src/
│   │   ├── app/                 # App router pages
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── lib/                 # Utilities and helpers
│   │   ├── stores/              # Zustand stores
│   │   ├── types/               # TypeScript types
│   │   └── locales/             # i18n translation files
│   ├── public/                  # Static assets
│   └── package.json
│
├── backend/                     # Python FastAPI backend
│   ├── app/
│   │   ├── api/                 # API routes
│   │   ├── core/                # Config, security, deps
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   ├── collectors/          # Data collection modules
│   │   └── workers/             # Celery tasks
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Test files
│   └── requirements.txt
│
├── docker-compose.yml           # Local development
├── .env.example                 # Environment variables template
└── README.md
```

---

## Prerequisites

- **Node.js** >= 18.0.0
- **Python** >= 3.11
- **PostgreSQL** >= 15
- **Redis** >= 7
- **Docker** & **Docker Compose** (optional, for containerized development)

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/trendpulse.git
cd trendpulse
```

### 2. Environment Setup

Copy the example environment file and configure your variables:

```bash
cp .env.example .env
```

Edit `.env` with your actual configuration values:
- Database credentials
- API keys (YouTube, Reddit)
- Secret keys for JWT
- Email service credentials (Resend/SendGrid)
- Telegram bot token (optional)

### 3. Option A: Docker Development (Recommended)

Start all services with Docker Compose:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- FastAPI backend (port 8000)
- Celery worker & beat scheduler
- Next.js frontend (port 3000)

Run database migrations:

```bash
docker-compose exec backend alembic upgrade head
```

### 4. Option B: Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

In separate terminals, start Celery worker and beat:

```bash
# Terminal 2 - Celery Worker
celery -A app.workers.celery_app worker --loglevel=info

# Terminal 3 - Celery Beat
celery -A app.workers.celery_app beat --loglevel=info
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## API Keys Setup

### YouTube Data API v3

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Add to `.env`: `YOUTUBE_API_KEY=your-key-here`

### Reddit API

1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Create a new app (select "script")
3. Copy client ID and secret
4. Add to `.env`:
   ```
   REDDIT_CLIENT_ID=your-client-id
   REDDIT_CLIENT_SECRET=your-client-secret
   ```

### Email Notifications (Resend)

1. Sign up at [Resend](https://resend.com/)
2. Create an API key
3. Add to `.env`: `RESEND_API_KEY=your-key-here`

---

## Development Commands

### Frontend

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking
```

### Backend

```bash
# Development
uvicorn app.main:app --reload

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1

# Testing
pytest
pytest --cov=app tests/

# Code formatting
black .
isort .
flake8 .
```

---

## Database Schema

The project uses Prisma schema as the source of truth. Key models include:

- **User**: Authentication and profile
- **Trend**: Discovered trending topics with scoring
- **TrendSnapshot**: Historical trend data
- **Favorite**: Saved trends with user notes
- **Alert**: User-configured notifications
- **SearchHistory**: User search tracking

See `schema.prisma` for the complete schema definition.

---

## Scoring Algorithm

The Opportunity Score (0-100) is calculated using:

| Factor | Weight | Description |
|--------|--------|-------------|
| Growth Rate | 35% | Percentage change over selected period |
| Volume | 25% | Relative search/discussion volume |
| Consistency | 20% | Steadiness of growth (not spiky) |
| Multi-Platform | 15% | Presence across multiple sources |
| Freshness | 5% | How recently trend emerged |

**Score Interpretation:**
- 80-100: Hot Opportunity (Act immediately)
- 60-79: Strong Potential (Good timing)
- 40-59: Worth Watching (Monitor closely)
- 20-39: Early Signal (Research more)
- 0-19: Low Priority (Minimal opportunity)

---

## Deployment

### Frontend (Vercel)

```bash
cd frontend
vercel deploy --prod
```

### Backend (Railway/Render)

1. Connect your repository
2. Set environment variables from `.env.example`
3. Deploy command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Database (Supabase/Neon)

1. Create a PostgreSQL database
2. Copy connection string to `DATABASE_URL`
3. Run migrations: `alembic upgrade head`

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## Documentation

- **PRD**: See `TrendPulse_PRD_v1.docx` for complete product requirements
- **Flowcharts**: See `TrendPulse_Flowcharts.md` for system architecture diagrams
- **Database Schema**: See `schema.prisma` for data models

---

## License

This project is proprietary and confidential.

---

## Support

For questions or issues, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ for entrepreneurs and digital creators**

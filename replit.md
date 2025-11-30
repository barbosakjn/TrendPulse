# TrendPulse - Replit Setup Documentation

## Project Overview
TrendPulse is a trend discovery platform for SaaS and digital products. It aggregates data from multiple sources (Google Trends, YouTube, Reddit) to provide actionable insights for entrepreneurs and content creators.

## Tech Stack
- **Frontend**: Next.js 14 with TypeScript, Tailwind CSS, shadcn/ui components
- **Backend**: FastAPI with Python 3.11
- **Database**: PostgreSQL (Replit built-in)
- **State Management**: Zustand
- **Data Fetching**: TanStack Query

## Recent Changes (November 30, 2025)
### YouTube Keyword Search
- Added YouTube search by keyword functionality (not just trending videos)
- YouTube now appears in Search Trends modal alongside AI Search, Google, and Reddit
- All 4 sources now support keyword-based search

### Google Trends Fix
- Migrated from `pytrends` to `trendspyg` library (pytrends was archived and returning 404 errors)
- Google Trends trending searches now work via RSS feed API
- Keyword interest feature temporarily unavailable (limitation of new library)
- Added deployment shell scripts to fix bash syntax errors

### Security Fixes
- Removed unused `decode_token()` function with `verify=False` (security vulnerability)

### Initial Replit Setup
1. Installed Python 3.11 and Node.js 20 modules
2. Created PostgreSQL database using Replit's built-in database
3. Installed all backend dependencies (FastAPI, SQLAlchemy, async PostgreSQL drivers, data collection libraries)
4. Installed all frontend dependencies (Next.js, React, Tailwind CSS, UI components)
5. Configured Next.js to run on port 5000 with host 0.0.0.0 for Replit proxy
6. Updated backend CORS to allow all origins for Replit environment
7. Set environment variables for database, API URLs, and JWT secrets
8. Ran database migrations successfully
9. Created workflows for both backend (port 8000) and frontend (port 5000)
10. Configured deployment settings for production

## Project Architecture
### Frontend (Port 5000)
- Entry point: `frontend/src/app/page.tsx` (home page)
- Auth pages: `/login` and `/register`
- Dashboard: `/dashboard`
- Next.js configured to bind to 0.0.0.0:5000 for Replit webview
- **API Proxy**: Next.js rewrites proxy all `/api/*` requests to backend at localhost:8000

### Backend (Port 8000)
- Entry point: `backend/app/main.py`
- API Documentation: http://localhost:8000/docs
- Auth endpoints: `/api/auth/*`
- Trends endpoints: `/api/trends/*`
- Database migrations: Alembic
- Runs on localhost:8000 (internal only, accessed via Next.js proxy)

### Database
- PostgreSQL managed by Replit
- Connection via DATABASE_URL environment variable
- Migrations handled by Alembic

## Environment Variables (Shared)
- `DATABASE_URL`: PostgreSQL connection string (auto-configured)
- `SECRET_KEY`: Application secret key
- `JWT_SECRET_KEY`: JWT signing key
- `JWT_ALGORITHM`: HS256
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 15
- `REFRESH_TOKEN_EXPIRE_DAYS`: 7
- `DEBUG`: True (development mode)

## Running the Application
### Development
Both workflows start automatically:
1. **Backend API**: Runs on localhost:8000 (internal only)
2. **Frontend**: Runs on 0.0.0.0:5000 (exposed via Replit webview)

### Access URLs
- Frontend: Accessible via Replit webview (port 5000)
- API: Proxied through Next.js at `/api/*` (browser -> Next.js:5000/api -> Backend:8000/api)
- Direct API access: Internal only at localhost:8000

## Dependencies
### Backend
- FastAPI, Uvicorn (web framework and server)
- SQLAlchemy, Alembic, psycopg (database ORM and migrations)
- Pydantic, pydantic-settings (data validation and configuration)
- python-jose, argon2-cffi (authentication and security)
- trendspyg (Google Trends data via RSS feed - replaces archived pytrends)
- praw, google-api-python-client (data collection services)
- pandas (data processing)

### Frontend
- Next.js 14, React 18 (framework)
- TypeScript (type safety)
- Tailwind CSS (styling)
- Radix UI components (accessible UI primitives)
- Zustand (state management)
- TanStack Query (data fetching)
- Axios (HTTP client)

## File Structure
```
/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/routes/   # API endpoints
│   │   ├── core/         # Config, database, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   ├── alembic/          # Database migrations
│   └── requirements.txt  # Python dependencies
├── frontend/             # Next.js frontend
│   ├── src/
│   │   ├── app/          # Next.js app router pages
│   │   ├── components/   # React components
│   │   ├── lib/          # Utilities and API client
│   │   └── stores/       # Zustand stores
│   ├── package.json      # Node dependencies
│   └── next.config.js    # Next.js configuration
└── replit.md            # This file

```

## Notes
- The backend uses async SQLAlchemy with psycopg (v3) for PostgreSQL
- Frontend and backend run on different ports (5000 and 8000)
- **API Architecture**: Frontend uses Next.js rewrites to proxy `/api/*` requests to the backend
  - Browser makes requests to the same origin (port 5000)
  - Next.js server-side proxies these to localhost:8000
  - Backend only needs to listen on localhost (not exposed externally)
- CORS is configured to allow localhost origins and Replit domain
- Cache-Control headers are set to prevent caching issues in Replit's iframe
- Deployment configured as VM type to support both frontend and backend
- Database migrations run automatically during deployment build phase

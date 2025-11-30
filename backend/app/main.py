"""
TrendPulse FastAPI Application Entry Point.
"""
from fastapi import FastAPI

from app.core.config import settings
from app.api.routes import auth, trends
from app.middleware import setup_cors

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="Trend Discovery Platform for SaaS & Digital Products",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
setup_cors(app)


# ============================================================================
# ROUTERS
# ============================================================================

# Authentication routes
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"],
)

# Trends routes
app.include_router(
    trends.router,
    prefix=f"{settings.API_V1_PREFIX}/trends",
    tags=["Google Trends"],
)


# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# ============================================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print(f"[START] {settings.APP_NAME} v{settings.APP_VERSION} starting up...")
    print(f"[DOCS] API Documentation: http://localhost:8000/docs")
    print(f"[AUTH] Auth endpoints: http://localhost:8000{settings.API_V1_PREFIX}/auth")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print(f"[STOP] {settings.APP_NAME} shutting down...")

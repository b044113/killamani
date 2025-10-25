"""
Killamani Platform - FastAPI Application

Main application entry point with all routes and middleware configured.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .infrastructure.config.settings import get_settings
from .infrastructure.api.routes import auth_routes, client_routes, chart_routes
from .infrastructure.api.middleware.error_handler import (
    domain_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)
from .domain.exceptions import DomainException

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="Killamani API",
    description="Professional Astrology Platform API with Hexagonal Architecture",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# ============================================================================
# CORS Configuration
# ============================================================================

# Parse CORS origins
# Temporarily allow all origins for testing
cors_origins = ["*"]
import sys
print(f"[DEBUG] Configured CORS Origins: {cors_origins}", file=sys.stderr, flush=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Exception Handlers
# ============================================================================

app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ============================================================================
# Routes
# ============================================================================

app.include_router(
    auth_routes.router,
    prefix="/api/auth",
    tags=["Authentication"]
)

app.include_router(
    client_routes.router,
    prefix="/api/clients",
    tags=["Clients"]
)

app.include_router(
    chart_routes.router,
    prefix="/api/charts",
    tags=["Charts"]
)

# ============================================================================
# Health Check
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns application status and version.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint.

    Returns API information.
    """
    return {
        "name": "Killamani API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health",
    }


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Actions to perform on application startup.
    """
    print("[STARTUP] Killamani API starting...")
    print(f"[INFO] Environment: {settings.ENVIRONMENT}")
    print(f"[INFO] Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    print(f"[INFO] CORS Origins: {settings.CORS_ORIGINS}")
    print("[OK] Application ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Actions to perform on application shutdown.
    """
    print("👋 Killamani API shutting down...")


# ============================================================================
# Development Runner
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

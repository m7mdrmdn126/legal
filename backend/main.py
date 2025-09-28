from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging
import sys
import os

# Add the current directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from routes.auth import router as auth_router
from routes.users import router as users_router
from routes.case_types import router as case_types_router
from routes.cases import router as cases_router
from routes.case_sessions import router as case_sessions_router
from routes.case_notes import router as case_notes_router
from routes.stats import router as stats_router
# Phase 4 - Polish Features
from routes.backup import router as backup_router
from routes.export import router as export_router
from routes.print import router as print_router
from routes.performance import router as performance_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="نظام إدارة القضايا القانونية - Legal Cases Management System",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Configure CORS for local network access
if settings.debug:
    # Development mode - allow all origins for local network
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins in debug mode
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    logger.info("CORS configured for development - allowing all origins")
else:
    # Production mode - use configured origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    logger.info(f"CORS configured for production - allowed origins: {settings.cors_origins}")

# Global exception handler for validation errors
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    errors = {}
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"])
        errors[field] = error["msg"]
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "detail": "خطأ في البيانات المدخلة",
            "error_code": "VALIDATION_ERROR",
            "field_errors": errors
        }
    )

# Global exception handler for HTTP exceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "detail": exc.detail,
            "error_code": "HTTP_ERROR"
        }
    )

# Global exception handler for general exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "detail": "حدث خطأ داخلي في الخادم",
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(case_types_router, prefix="/api/v1")
app.include_router(cases_router, prefix="/api/v1")
app.include_router(case_sessions_router, prefix="/api/v1")
app.include_router(case_notes_router, prefix="/api/v1")
app.include_router(stats_router, prefix="/api/v1")
# Phase 4 - Polish Features
app.include_router(backup_router, prefix="/api/v1")
app.include_router(export_router, prefix="/api/v1")
app.include_router(print_router, prefix="/api/v1")
app.include_router(performance_router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "مرحباً بك في نظام إدارة القضايا القانونية",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "Documentation disabled in production"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "legal-cases-api",
        "version": settings.app_version
    }

# API info endpoint
@app.get("/api/v1/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "نظام إدارة القضايا القانونية",
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "case_types": "/api/v1/case-types",
            "cases": "/api/v1/cases",
            "case_sessions": "/api/v1/case-sessions",
            "case_notes": "/api/v1/case-notes",
            "stats": "/api/v1/stats",
            "backup": "/api/v1/backup",
            "export": "/api/v1/export",
            "print": "/api/v1/print",
            "performance": "/api/v1/performance"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )

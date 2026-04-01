from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os

from config import CONFIG, setup_logging

# Setup logging
logger = setup_logging()

from middleware.error_handler import (
    general_exception_handler,
    integrity_error_handler,
    jwt_expired_handler,
    jwt_invalid_handler,
    validation_error_handler
)
from middleware.rate_limiter import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.exc import IntegrityError
from jwt import ExpiredSignatureError, InvalidTokenError
from pydantic import ValidationError

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting RealtyAI application...")
    # Initialize rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    yield
    # Shutdown
    logger.info("Shutting down RealtyAI application...")

app = FastAPI(
    title="RealtyAI",
    description="AI-powered real estate listing platform",
    version="1.0.0",
    lifespan=lifespan
)

# Register exception handlers
app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(ExpiredSignatureError, jwt_expired_handler)
app.add_exception_handler(InvalidTokenError, jwt_invalid_handler)
app.add_exception_handler(ValidationError, validation_error_handler)

# CORS Configuration - restricted methods and headers
allowed_origins = CONFIG.get('cors', {}).get('allowed_origins', [
    "http://localhost:3000",
    "http://localhost:8000"
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],  # Restricted methods
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "Accept",
        "Origin"
    ],  # Restricted headers
    expose_headers=["X-Request-ID"],
    max_age=600
)

# Add rate limiting middleware
app.add_middleware(SlowAPIMiddleware)

from routes import auth, oauth, users, listings, images, descriptions, maps
from routes.admin import config as admin_config, features as admin_features, filters as admin_filters

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(oauth.router, prefix="/api/oauth", tags=["OAuth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(listings.router, prefix="/api/listings", tags=["Listings"])
app.include_router(images.router, prefix="/api/images", tags=["Images"])
app.include_router(descriptions.router, prefix="/api/descriptions", tags=["Descriptions"])
app.include_router(maps.router, prefix="/api/maps", tags=["Maps"])
app.include_router(admin_config.router, prefix="/api/admin/config", tags=["Admin"])
app.include_router(admin_features.router, prefix="/api/admin/features", tags=["Admin"])
app.include_router(admin_filters.router, prefix="/api/admin/filters", tags=["Admin"])

uploads_dir = os.path.join(os.path.dirname(__file__), CONFIG.get('images', {}).get('uploads_dir', './uploads'))
os.makedirs(uploads_dir, exist_ok=True)

if os.path.exists(uploads_dir):
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.get("/")
async def root():
    return {
        "name": "RealtyAI API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

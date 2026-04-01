from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi import Limiter
import logging

from config import CONFIG

logger = logging.getLogger(__name__)

# Initialize rate limiter
# Use 60 requests per minute for general endpoints
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60 per minute"],
    storage_uri="memory://",
    retry_after="default"
)

# Register the rate limit exceeded handler
def rate_limit_exceeded_handler(request, exc):
    """Custom handler for rate limit exceeded"""
    from fastapi import status
    from fastapi.responses import JSONResponse
    
    logger.warning(f"Rate limit exceeded for IP: {get_remote_address(request)}")
    
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": "Too many requests. Please try again later.",
            "error": "rate_limit_exceeded"
        }
    )

# Rate limit configurations
RATE_LIMITS = {
    # Authentication endpoints - strict limits to prevent brute force
    "login": "5 per minute",
    "register": "3 per minute",
    "password_reset": "3 per hour",
    
    # General API endpoints
    "general": "60 per minute",
    
    # Admin endpoints - more restrictive
    "admin": "30 per minute",
    
    # Image upload - very restrictive
    "upload": "10 per minute",
    
    # AI description generation - expensive operation
    "ai_generation": "5 per minute",
}

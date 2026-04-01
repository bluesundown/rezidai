import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from jwt import ExpiredSignatureError, InvalidTokenError
from pydantic import ValidationError
from config import CONFIG

logger = logging.getLogger(__name__)

def is_production() -> bool:
    """Check if application is running in production environment"""
    return CONFIG.get('environment', 'development') == 'production'

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions - never expose details in production"""
    error_msg = str(exc)
    
    # Log full error details for debugging
    logger.error(f"Internal server error: {error_msg}", exc_info=True)
    
    # In production, return generic error message
    if is_production():
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error. Please contact support if the problem persists."}
        )
    
    # In development, include error details for debugging
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "error": error_msg}
    )

async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors"""
    error_msg = str(exc)
    
    logger.error(f"Database integrity error: {error_msg}", exc_info=True)
    
    # Never expose database structure in errors
    if is_production():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Invalid request. Please check your data and try again."}
        )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Database integrity error", "error": "Duplicate or invalid data"}
    )

async def jwt_expired_handler(request: Request, exc: ExpiredSignatureError):
    """Handle expired JWT tokens"""
    logger.warning("JWT token expired")
    
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Authentication token has expired. Please log in again."},
        headers={"WWW-Authenticate": "Bearer"},
    )

async def jwt_invalid_handler(request: Request, exc: InvalidTokenError):
    """Handle invalid JWT tokens"""
    logger.warning(f"Invalid JWT token: {type(exc).__name__}")
    
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Invalid authentication token. Please log in again."},
        headers={"WWW-Authenticate": "Bearer"},
    )

async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors with user-friendly messages"""
    logger.debug(f"Validation error: {exc.errors()}")
    
    # Format validation errors in a user-friendly way
    errors = []
    for error in exc.errors():
        field = error.get('loc', ['unknown'])[0]
        message = error.get('msg', 'Validation error')
        
        # Make error messages more user-friendly
        if 'min_length' in message.lower():
            min_len = error.get('ctx', {}).get('field', 'required')
            message = f"{field} is too short"
        elif 'max_length' in message.lower():
            message = f"{field} is too long"
        elif 'email' in message.lower():
            message = f"{field} must be a valid email address"
        elif 'password' in message.lower():
            # Don't expose password validation details in production
            if is_production():
                message = "Password does not meet requirements"
            else:
                message = f"Password: {message}"
        
        errors.append({
            "field": field,
            "message": message
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": errors}
    )

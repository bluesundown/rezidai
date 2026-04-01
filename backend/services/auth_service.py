import bcrypt
import jwt
from datetime import datetime, timedelta
from config import CONFIG

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(hours=CONFIG['auth']['jwt_expiration_hours'])
    )
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        CONFIG['auth']['jwt_secret'],
        algorithm=CONFIG['auth'].get('algorithm', 'HS256')
    )
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            CONFIG['auth']['jwt_secret'],
            algorithms=[CONFIG['auth'].get('algorithm', 'HS256')]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def generate_email_verification_token(user_id: str) -> str:
    return create_access_token(
        {"sub": user_id, "type": "email_verification"},
        expires_delta=timedelta(hours=24)
    )

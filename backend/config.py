import os
import logging
import yaml
from dotenv import load_dotenv

load_dotenv()

# Configure logging
def setup_logging():
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def load_config():
    config_path = os.getenv('CONFIG_PATH', 'config.yaml')
    if not os.path.exists(config_path):
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in config file: {e}")
        raise
    
    override_with_env(config)
    validate_config(config)
    return config

def override_with_env(config):
    """Override config values with environment variables for security"""
    
    # Database - Support both individual vars and DATABASE_URL (for Render/Heroku)
    if os.getenv('DATABASE_URL'):
        # Parse DATABASE_URL format: postgresql://user:pass@host:port/dbname
        from urllib.parse import urlparse
        parsed = urlparse(os.getenv('DATABASE_URL'))
        config['database']['type'] = 'postgresql'
        config['database']['host'] = parsed.hostname
        config['database']['port'] = int(parsed.port or 5432)
        config['database']['name'] = parsed.path.lstrip('/')
        config['database']['user'] = parsed.username
        config['database']['password'] = parsed.password or ''
    else:
        # Individual environment variables
        if os.getenv('DATABASE_TYPE'):
            config['database']['type'] = os.getenv('DATABASE_TYPE')
        if os.getenv('DATABASE_HOST'):
            config['database']['host'] = os.getenv('DATABASE_HOST')
        if os.getenv('DATABASE_PORT'):
            config['database']['port'] = int(os.getenv('DATABASE_PORT'))
        if os.getenv('DATABASE_NAME'):
            config['database']['name'] = os.getenv('DATABASE_NAME')
        if os.getenv('DATABASE_USER'):
            config['database']['user'] = os.getenv('DATABASE_USER')
        if os.getenv('DATABASE_PASSWORD'):
            config['database']['password'] = os.getenv('DATABASE_PASSWORD')
    
    # Authentication
    if os.getenv('JWT_SECRET'):
        config['auth']['jwt_secret'] = os.getenv('JWT_SECRET')
    if os.getenv('JWT_EXPIRATION_HOURS'):
        config['auth']['jwt_expiration_hours'] = int(os.getenv('JWT_EXPIRATION_HOURS'))
    
    # API Keys
    if os.getenv('QWEN_API_KEY'):
        config['api']['qwen_api_key'] = os.getenv('QWEN_API_KEY')
    if os.getenv('QWEN_ENDPOINT'):
        config['api']['qwen_endpoint'] = os.getenv('QWEN_ENDPOINT')
    if os.getenv('QWEN_MODEL'):
        config['api']['qwen_model'] = os.getenv('QWEN_MODEL')
    if os.getenv('GOOGLE_MAPS_API_KEY'):
        config['api']['google_maps_api_key'] = os.getenv('GOOGLE_MAPS_API_KEY')
    
    # Stripe
    if os.getenv('STRIPE_SECRET_KEY'):
        config['api']['stripe_secret_key'] = os.getenv('STRIPE_SECRET_KEY')
    if os.getenv('STRIPE_WEBHOOK_SECRET'):
        config['api']['stripe_webhook_secret'] = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    # OAuth - Google
    if os.getenv('GOOGLE_OAUTH_CLIENT_ID'):
        config['api']['oauth']['google']['client_id'] = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
    if os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'):
        config['api']['oauth']['google']['client_secret'] = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
    
    # OAuth - Apple
    if os.getenv('APPLE_TEAM_ID'):
        config['api']['oauth']['apple']['team_id'] = os.getenv('APPLE_TEAM_ID')
    if os.getenv('APPLE_CLIENT_ID'):
        config['api']['oauth']['apple']['client_id'] = os.getenv('APPLE_CLIENT_ID')
    if os.getenv('APPLE_CLIENT_SECRET'):
        config['api']['oauth']['apple']['client_secret'] = os.getenv('APPLE_CLIENT_SECRET')
    
    # Mock Services
    if os.getenv('MOCK_SERVICES_ENABLED') is not None:
        config['mock_services']['enabled'] = os.getenv('MOCK_SERVICES_ENABLED', 'false').lower() == 'true'
    if os.getenv('MOCK_AI_RESPONSES') is not None:
        config['mock_services']['ai_responses'] = os.getenv('MOCK_AI_RESPONSES', 'false').lower() == 'true'
    if os.getenv('MOCK_MAPS_RESPONSES') is not None:
        config['mock_services']['maps_responses'] = os.getenv('MOCK_MAPS_RESPONSES', 'false').lower() == 'true'
    if os.getenv('MOCK_STRIPE_ENABLED') is not None:
        config['mock_services']['stripe_enabled'] = os.getenv('MOCK_STRIPE_ENABLED', 'false').lower() == 'true'
    if os.getenv('MOCK_OAUTH_VALIDATION') is not None:
        config['mock_services']['oauth_validation'] = os.getenv('MOCK_OAUTH_VALIDATION', 'false').lower() == 'true'
    
    # CORS
    if os.getenv('CORS_ALLOWED_ORIGINS'):
        origins = os.getenv('CORS_ALLOWED_ORIGINS').split(',')
        config['cors']['allowed_origins'] = [origin.strip() for origin in origins]
    
    # Environment
    config['environment'] = os.getenv('ENVIRONMENT', 'development')

def validate_config(config):
    """Validate critical configuration values"""
    environment = config.get('environment', 'development')
    
    # Warn if JWT secret is default
    if config['auth']['jwt_secret'] == 'change_this_secret_key_in_production_make_it_long_and_random':
        if environment == 'production':
            logger.error("CRITICAL: Default JWT secret in production! Change immediately!")
            raise ValueError("JWT_SECRET must be changed in production")
        else:
            logger.warning("WARNING: Using default JWT secret. Change before production!")
    
    # Warn if mock services are enabled in production
    if config['mock_services']['enabled'] and environment == 'production':
        logger.error("CRITICAL: Mock services enabled in production!")
        raise ValueError("Mock services must be disabled in production")
    
    # Warn if API keys are placeholders
    if 'YOUR_' in config['api']['qwen_api_key'] or config['api']['qwen_api_key'] == '':
        logger.warning("WARNING: QWEN_API_KEY not configured!")
    if 'YOUR_' in config['api']['google_maps_api_key'] or config['api']['google_maps_api_key'] == '':
        logger.warning("WARNING: GOOGLE_MAPS_API_KEY not configured!")

CONFIG = load_config()

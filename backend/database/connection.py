from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import CONFIG

def get_database_url():
    db_config = CONFIG.get('database', {})
    db_type = db_config.get('type', 'sqlite')
    
    if db_type == 'sqlite':
        db_path = db_config.get('path', 'sqlite:///realtyai.db')
        return db_path
    else:
        host = db_config.get('host', 'localhost')
        port = db_config.get('port', 5432)
        name = db_config.get('name', 'realtyai')
        user = db_config.get('user', 'postgres')
        password = db_config.get('password', 'postgres')
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"

DATABASE_URL = get_database_url()

if 'sqlite' in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # PostgreSQL with connection pooling for production
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Test connections before using
        pool_size=10,
        max_overflow=20,
        pool_timeout=30
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

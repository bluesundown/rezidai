import secrets
import string
import logging
from sqlalchemy.orm import Session
from models.user import User
from models.ai_filter import AIFilter
from services.auth_service import hash_password

logger = logging.getLogger(__name__)

def generate_strong_password(length: int = 16) -> str:
    """Generate a cryptographically strong random password"""
    # Ensure password has at least one of each required character type
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*()_+-=")
    ]
    
    # Fill the rest with random characters
    all_chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    password.extend(secrets.choice(all_chars) for _ in range(length - 4))
    
    # Shuffle the password
    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)
    
    return ''.join(password_list)

def seed_database(db: Session):
    admin_user = db.query(User).filter(User.email == "admin@realtyai.com").first()
    
    if not admin_user:
        # Generate a strong random password
        temp_password = generate_strong_password(16)
        
        admin = User(
            email="admin@realtyai.com",
            password_hash=hash_password(temp_password),
            first_name="Admin",
            last_name="User",
            is_admin=True,
            email_verified=True,
            must_change_password=True  # Force password change on first login
        )
        db.add(admin)
        db.commit()
        
        logger.info("Created admin user: admin@realtyai.com")
        logger.info(f"Temporary password: {temp_password}")
        logger.warning("IMPORTANT: Please change the admin password immediately after first login!")
        print("\n" + "="*60)
        print("ADMIN USER CREATED")
        print("="*60)
        print(f"Email:         admin@realtyai.com")
        print(f"Password:      {temp_password}")
        print("="*60)
        print("WARNING: Please change the password immediately after first login!")
        print("="*60 + "\n")
    else:
        logger.info("Admin user already exists")
    
    default_filters = [
        {
            "name": "Professional",
            "slug": "professional",
            "description": "Formal and business-oriented description",
            "tone": "professional",
            "focus": "general",
            "is_default": True,
            "display_order": 0
        },
        {
            "name": "Friendly",
            "slug": "friendly",
            "description": "Warm and inviting description",
            "tone": "friendly",
            "focus": "family",
            "is_default": False,
            "display_order": 1
        },
        {
            "name": "Luxury",
            "slug": "luxury",
            "description": "Elegant and sophisticated description",
            "tone": "luxury",
            "focus": "luxury",
            "is_default": False,
            "display_order": 2
        },
        {
            "name": "Modern",
            "slug": "modern",
            "description": "Contemporary and sleek description",
            "tone": "modern",
            "focus": "amenities",
            "is_default": False,
            "display_order": 3
        }
    ]
    
    for filter_data in default_filters:
        existing = db.query(AIFilter).filter(AIFilter.slug == filter_data['slug']).first()
        if not existing:
            filter = AIFilter(**filter_data)
            db.add(filter)
            logger.info(f"Created AI filter: {filter_data['name']}")
    
    db.commit()
    logger.info("Database seeded successfully!")

if __name__ == "__main__":
    from database.connection import SessionLocal
    with SessionLocal() as db:
        seed_database(db)

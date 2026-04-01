"""Initial migration - create all tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = ['initial']
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('profile_photo_url', sa.String(500), nullable=True),
        sa.Column('oauth_provider', sa.String(50), nullable=True),
        sa.Column('oauth_id', sa.String(255), nullable=True),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True),
        sa.Column('subscription_tier', sa.String(50), default='free'),
        sa.Column('subscription_status', sa.String(50), default='inactive'),
        sa.Column('is_admin', sa.Boolean, default=False),
        sa.Column('email_verified', sa.Boolean, default=False),
        sa.Column('email_verified_at', sa.DateTime, nullable=True),
        sa.Column('email_verification_token', sa.String(255), nullable=True),
        sa.Column('must_change_password', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('last_login_at', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
    )
    
    # Create index on email
    op.create_index('idx_users_email', 'users', ['email'])
    
    # Create listings table
    op.create_table(
        'listings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('property_type', sa.String(100), nullable=False),
        sa.Column('address', sa.String(500), nullable=False),
        sa.Column('city', sa.String(200), nullable=False),
        sa.Column('state', sa.String(100), nullable=False),
        sa.Column('zip_code', sa.String(20), nullable=False),
        sa.Column('country', sa.String(100), default='USA'),
        sa.Column('price', sa.Integer, nullable=False),
        sa.Column('bedrooms', sa.Integer, nullable=True),
        sa.Column('bathrooms', sa.Numeric(3, 1), nullable=True),
        sa.Column('square_feet', sa.Integer, nullable=True),
        sa.Column('lot_size', sa.String(100), nullable=True),
        sa.Column('year_built', sa.Integer, nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('ai_description', sa.Text, nullable=True),
        sa.Column('latitude', sa.Numeric(10, 8), nullable=True),
        sa.Column('longitude', sa.Numeric(11, 8), nullable=True),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('views', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    op.create_index('idx_listings_user_id', 'listings', ['user_id'])
    op.create_index('idx_listings_status', 'listings', ['status'])
    op.create_index('idx_listings_property_type', 'listings', ['property_type'])
    
    # Create images table
    op.create_table(
        'images',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('listing_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('thumbnail_path', sa.String(500), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('file_size', sa.Integer, nullable=False),
        sa.Column('width', sa.Integer, nullable=False),
        sa.Column('height', sa.Integer, nullable=False),
        sa.Column('display_order', sa.Integer, default=0),
        sa.Column('is_primary', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.ForeignKeyConstraint(['listing_id'], ['listings.id'], ondelete='CASCADE'),
    )
    
    op.create_index('idx_images_listing_id', 'images', ['listing_id'])
    
    # Create ai_filters table
    op.create_table(
        'ai_filters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('tone', sa.String(50), nullable=True),
        sa.Column('focus', sa.String(100), nullable=True),
        sa.Column('prompt_template', sa.Text, nullable=True),
        sa.Column('parameters', sa.JSON, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_default', sa.Boolean, default=False),
        sa.Column('display_order', sa.Integer, default=0),
        sa.Column('usage_count', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    op.create_index('idx_ai_filters_slug', 'ai_filters', ['slug'])


def downgrade():
    # Drop tables in reverse order
    op.drop_table('ai_filters')
    op.drop_table('images')
    op.drop_table('listings')
    op.drop_table('users')

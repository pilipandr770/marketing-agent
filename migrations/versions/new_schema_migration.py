"""Add marketing_agent schema

Revision ID: marketing_agent_schema
Revises: 
Create Date: 2025-10-08 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'marketing_agent_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create schema
    op.execute('CREATE SCHEMA IF NOT EXISTS marketing_agent')
    
    # Create user table
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('telegram_token', sa.String(length=256), nullable=True),
    sa.Column('telegram_chat_id', sa.String(length=128), nullable=True),
    sa.Column('facebook_access_token', sa.String(length=512), nullable=True),
    sa.Column('facebook_page_id', sa.String(length=128), nullable=True),
    sa.Column('linkedin_access_token', sa.String(length=512), nullable=True),
    sa.Column('instagram_access_token', sa.String(length=512), nullable=True),
    sa.Column('openai_vector_store_id', sa.String(length=128), nullable=True),
    sa.Column('openai_system_prompt', sa.Text(), nullable=True),
    sa.Column('openai_api_key', sa.String(length=256), nullable=True),
    sa.Column('stripe_customer_id', sa.String(length=64), nullable=True),
    sa.Column('stripe_subscription_id', sa.String(length=64), nullable=True),
    sa.Column('plan', sa.String(length=32), nullable=True),
    sa.Column('plan_expires_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='marketing_agent'
    )
    op.create_index(op.f('ix_marketing_agent_user_email'), 'user', ['email'], unique=True, schema='marketing_agent')
    
    # Create schedule table
    op.create_table('schedule',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('cron_expression', sa.String(length=64), nullable=False),
    sa.Column('timezone', sa.String(length=64), nullable=True),
    sa.Column('channel', sa.String(length=64), nullable=False),
    sa.Column('content_template', sa.Text(), nullable=False),
    sa.Column('generate_image', sa.Boolean(), nullable=True),
    sa.Column('generate_voice', sa.Boolean(), nullable=True),
    sa.Column('content_type', sa.String(length=32), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('last_run', sa.DateTime(), nullable=True),
    sa.Column('next_run', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['marketing_agent.user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='marketing_agent'
    )
    
    # Create file_asset table
    op.create_table('file_asset',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('original_filename', sa.String(length=255), nullable=False),
    sa.Column('file_size', sa.Integer(), nullable=True),
    sa.Column('mime_type', sa.String(length=128), nullable=True),
    sa.Column('openai_file_id', sa.String(length=128), nullable=True),
    sa.Column('vector_store_id', sa.String(length=128), nullable=True),
    sa.Column('processing_status', sa.String(length=32), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['marketing_agent.user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='marketing_agent'
    )
    
    # Create generated_content table
    op.create_table('generated_content',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('schedule_id', sa.Integer(), nullable=True),
    sa.Column('text_content', sa.Text(), nullable=False),
    sa.Column('image_url', sa.String(length=512), nullable=True),
    sa.Column('voice_url', sa.String(length=512), nullable=True),
    sa.Column('channel', sa.String(length=64), nullable=False),
    sa.Column('published', sa.Boolean(), nullable=True),
    sa.Column('published_at', sa.DateTime(), nullable=True),
    sa.Column('publication_response', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['schedule_id'], ['marketing_agent.schedule.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['marketing_agent.user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='marketing_agent'
    )


def downgrade():
    op.drop_table('generated_content', schema='marketing_agent')
    op.drop_table('file_asset', schema='marketing_agent')
    op.drop_table('schedule', schema='marketing_agent')
    op.drop_index(op.f('ix_marketing_agent_user_email'), table_name='user', schema='marketing_agent')
    op.drop_table('user', schema='marketing_agent')
    op.execute('DROP SCHEMA IF EXISTS marketing_agent CASCADE')

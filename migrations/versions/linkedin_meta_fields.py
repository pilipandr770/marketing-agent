"""Add LinkedIn and Meta platform fields

Revision ID: linkedin_meta_fields
Revises: marketing_agent_schema
Create Date: 2025-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'linkedin_meta_fields'
down_revision = 'marketing_agent_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Add new LinkedIn fields
    op.add_column('user', sa.Column('linkedin_urn', sa.String(length=256), nullable=True), schema='marketing_agent')
    
    # Add new Meta platform fields
    op.add_column('user', sa.Column('meta_access_token', sa.String(length=512), nullable=True), schema='marketing_agent')
    
    # Note: facebook_page_id already exists in the schema
    # Note: instagram_business_id should be added
    op.add_column('user', sa.Column('instagram_business_id', sa.String(length=128), nullable=True), schema='marketing_agent')
    
    # Old fields (facebook_access_token, linkedin_access_token, instagram_access_token) remain for backward compatibility
    # They can be removed in a future migration after data is migrated to new fields


def downgrade():
    # Remove new fields
    op.drop_column('user', 'instagram_business_id', schema='marketing_agent')
    op.drop_column('user', 'meta_access_token', schema='marketing_agent')
    op.drop_column('user', 'linkedin_urn', schema='marketing_agent')

"""add models and datasets tables

Revision ID: xxxxxxxxxxxx
Revises: previous_revision_id
Create Date: 2024-xx-xx

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

def upgrade():
    # Models Tabelle
    op.create_table(
        'models',
        sa.Column('id', sa.Text(), primary_key=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('project_id', sa.Text(), nullable=False),
        sa.Column('type', sa.Text(), nullable=False),
        sa.Column('version', sa.Text(), server_default='1.0'),
        sa.Column('metrics', JSONB(), server_default='{}'),
        sa.Column('parameters', JSONB(), server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    # Datasets Tabelle
    op.create_table(
        'datasets',
        sa.Column('id', sa.Text(), primary_key=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('project_id', sa.Text(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('image_count', sa.Integer(), server_default='0'),
        sa.Column('processed_count', sa.Integer(), server_default='0'),
        sa.Column('dataset_metadata', JSONB(), server_default='{}'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'))
    )

def downgrade():
    op.drop_table('datasets')
    op.drop_table('models') 
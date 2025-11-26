"""Add RAG/CAG fields to semantic_models

Revision ID: add_rag_cag_fields
Revises: 
Create Date: 2025-11-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_rag_cag_fields'
down_revision = '000_initial_schema'
depends_on = None


def upgrade():
    # Add new columns to semantic_models table
    op.add_column('semantic_models', sa.Column('system_prompt', sa.Text(), nullable=True))
    op.add_column('semantic_models', sa.Column('user_prompt_template', sa.Text(), nullable=True))
    op.add_column('semantic_models', sa.Column('business_glossary', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('semantic_models', sa.Column('example_queries', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('semantic_models', sa.Column('auto_generated_context', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('semantic_models', sa.Column('prompt_version', sa.Integer(), nullable=True, server_default='1'))


def downgrade():
    # Remove columns if rolling back
    op.drop_column('semantic_models', 'prompt_version')
    op.drop_column('semantic_models', 'auto_generated_context')
    op.drop_column('semantic_models', 'example_queries')
    op.drop_column('semantic_models', 'business_glossary')
    op.drop_column('semantic_models', 'user_prompt_template')
    op.drop_column('semantic_models', 'system_prompt')

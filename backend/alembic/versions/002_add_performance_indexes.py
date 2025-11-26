"""Add performance indexes

Revision ID: 002_add_performance_indexes
Revises: add_rag_cag_fields
Create Date: 2025-11-26

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_performance_indexes'
down_revision = 'add_rag_cag_fields'
depends_on = None


def upgrade():
    # Add indexes for frequently queried timestamp columns
    op.create_index('ix_chat_messages_created_at', 'chat_messages', ['created_at'], unique=False)
    op.create_index('ix_chat_sessions_created_at', 'chat_sessions', ['created_at'], unique=False)
    op.create_index('ix_chat_sessions_updated_at', 'chat_sessions', ['updated_at'], unique=False)

    # Add composite indexes for common query patterns
    op.create_index(
        'ix_chat_sessions_user_connection',
        'chat_sessions',
        ['user_id', 'connection_id'],
        unique=False
    )

    op.create_index(
        'ix_chat_messages_session_created',
        'chat_messages',
        ['session_id', 'created_at'],
        unique=False
    )

    # Add index for semantic model lookups
    op.create_index('ix_semantic_models_table_name', 'semantic_models', ['table_name'], unique=False)

    # Add index for active connections filter
    op.create_index(
        'ix_database_connections_active_owner',
        'database_connections',
        ['is_active', 'owner_id'],
        unique=False
    )

    # Add index for document embeddings by connection
    op.create_index('ix_document_embeddings_connection_id', 'document_embeddings', ['connection_id'], unique=False)

    # Add index for LLM configurations
    op.create_index('ix_llm_configurations_active', 'llm_configurations', ['is_active'], unique=False)
    op.create_index('ix_llm_configurations_provider', 'llm_configurations', ['provider'], unique=False)


def downgrade():
    # Drop indexes in reverse order
    op.drop_index('ix_llm_configurations_provider', table_name='llm_configurations')
    op.drop_index('ix_llm_configurations_active', table_name='llm_configurations')
    op.drop_index('ix_document_embeddings_connection_id', table_name='document_embeddings')
    op.drop_index('ix_database_connections_active_owner', table_name='database_connections')
    op.drop_index('ix_semantic_models_table_name', table_name='semantic_models')
    op.drop_index('ix_chat_messages_session_created', table_name='chat_messages')
    op.drop_index('ix_chat_sessions_user_connection', table_name='chat_sessions')
    op.drop_index('ix_chat_sessions_updated_at', table_name='chat_sessions')
    op.drop_index('ix_chat_sessions_created_at', table_name='chat_sessions')
    op.drop_index('ix_chat_messages_created_at', table_name='chat_messages')

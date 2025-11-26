from app.db.session import engine
from app.db.base import Base
from app.models.models import *
from sqlalchemy import text

# Enable pgvector extension
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()
    print("✅ pgvector extension enabled")

# Create all tables
Base.metadata.create_all(bind=engine)
print("✅ All database tables created successfully!")

# List created tables
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename
    """))
    tables = [row[0] for row in result]
    print(f"\n📊 Created {len(tables)} tables:")
    for table in tables:
        print(f"  - {table}")

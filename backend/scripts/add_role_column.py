import sys
import os
from sqlalchemy import create_engine, text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def add_role_column():
    """Add role column to users table if it doesn't exist"""
    engine = create_engine(settings.assemble_db_url())
    
    with engine.connect() as conn:
        try:
            # Check if column exists
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='role'"))
            if result.fetchone():
                print("Column 'role' already exists.")
                return

            # Add column
            print("Adding 'role' column to users table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'user'"))
            conn.commit()
            print("Successfully added 'role' column.")
            
            # Update existing superusers to have admin role
            print("Updating superusers to have 'admin' role...")
            conn.execute(text("UPDATE users SET role = 'admin' WHERE is_superuser = true"))
            conn.commit()
            print("Successfully updated superusers.")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    add_role_column()

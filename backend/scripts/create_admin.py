import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.models.models import User
from app.core.security import get_password_hash

def create_admin_user():
    """Create a default admin user"""
    engine = create_engine(settings.assemble_db_url())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if admin:
            print("Admin user already exists.")
            # Ensure role is admin
            if admin.role != "admin":
                admin.role = "admin"
                admin.is_superuser = True
                db.commit()
                print("Updated existing admin user role.")
            return

        # Create admin
        print("Creating admin user...")
        new_admin = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            is_active=True,
            is_superuser=True
        )
        db.add(new_admin)
        db.commit()
        print("Successfully created admin user.")
        print("Email: admin@example.com")
        print("Username: admin")
        print("Password: admin123")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()

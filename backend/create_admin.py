"""
Create admin account for testing
Run: python create_admin.py
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.schemas import User
from auth import hash_password
from database import Base, settings

# Create database connection
engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Admin credentials
ADMIN_EMAIL = "admin@savefood.local"
ADMIN_PASSWORD = "Admin123!@#"
ADMIN_NAME = "Admin User"

try:
    # Check if admin already exists
    existing_admin = session.query(User).filter(User.email == ADMIN_EMAIL).first()
    if existing_admin:
        print(f"✓ Admin already exists: {ADMIN_EMAIL}")
        print(f"  Password: {ADMIN_PASSWORD}")
        session.close()
        exit(0)
    
    # Create admin user
    admin_user = User(
        name=ADMIN_NAME,
        email=ADMIN_EMAIL,
        password_hash=hash_password(ADMIN_PASSWORD),
        role="admin",
        is_verified=True,
        avatar="🔐"
    )
    
    session.add(admin_user)
    session.commit()
    
    print("✅ Admin account created successfully!")
    print(f"   Email: {ADMIN_EMAIL}")
    print(f"   Password: {ADMIN_PASSWORD}")
    print(f"   Role: admin")
    print("\nYou can now log in with these credentials.")
    
except Exception as e:
    session.rollback()
    print(f"❌ Error creating admin: {e}")
finally:
    session.close()

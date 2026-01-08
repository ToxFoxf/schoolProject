"""
Simple admin creation script - standalone
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from bcrypt import hashpw, gensalt

# Database URL from env or default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/savefood")

# Hashing function
def hash_password(password: str) -> str:
    return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

try:
    # Connect to database
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check if admin exists
    result = session.execute(text("SELECT id FROM users WHERE email = :email"), 
                            {"email": "admin@savefood.local"})
    if result.fetchone():
        print("✓ Admin already exists: admin@savefood.local")
        session.close()
        sys.exit(0)
    
    # Create admin user
    hashed_pwd = hash_password("Admin123!@#")
    session.execute(
        text("""
        INSERT INTO users (name, email, password_hash, role, is_verified, avatar, created_at)
        VALUES (:name, :email, :password_hash, :role, :is_verified, :avatar, NOW())
        """),
        {
            "name": "Admin User",
            "email": "admin@savefood.local",
            "password_hash": hashed_pwd,
            "role": "admin",
            "is_verified": True,
            "avatar": "🔐"
        }
    )
    session.commit()
    
    print("✅ Admin account created!")
    print("   Email: admin@savefood.local")
    print("   Password: Admin123!@#")
    print("   Role: admin")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
finally:
    session.close()

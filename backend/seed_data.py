"""Database seed script to populate test data"""

from database import SessionLocal, engine, Base
from models import UserDB, ProjectDB
from auth import hash_password
import crud


def seed_database():
    """Populate database with test data"""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if test user already exists
        existing_user = crud.get_user_by_email(db, "donor@example.com")
        if existing_user:
            print("✓ Test user already exists")
            user_id = existing_user.id
        else:
            # Create test user
            test_user = UserDB(
                email="donor@example.com",
                name="Test User",
                password_hash=hash_password("password123"),
                avatar="👤",
                xp=0,
                rating_level="Bronze",
                is_admin=False
            )
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            user_id = test_user.id
            
            print("✓ Test user created successfully")
            print(f"  Email: donor@example.com")
            print(f"  Password: password123")
            print(f"  User ID: {user_id}")
        
        # Check if sample projects exist
        existing_projects = db.query(ProjectDB).filter(ProjectDB.owner_id == user_id).count()
        if existing_projects > 0:
            print(f"✓ Sample projects already exist ({existing_projects} projects)")
            return
        
        # Create sample projects
        projects_data = [
            {
                "name": "Food Distribution Center",
                "description": "Distribute food to local communities in need",
                "icon": "🍕",
                "color": "#ef4444",
                "goal_amount": 5000.0,
                "owner_id": user_id
            },
            {
                "name": "School Meal Program",
                "description": "Provide nutritious meals to school children",
                "icon": "🍎",
                "color": "#10b981",
                "goal_amount": 10000.0,
                "owner_id": user_id
            },
            {
                "name": "Senior Care Meals",
                "description": "Home-delivered meals for elderly residents",
                "icon": "🥗",
                "color": "#3b82f6",
                "goal_amount": 7500.0,
                "owner_id": user_id
            },
            {
                "name": "Emergency Food Relief",
                "description": "Rapid response food distribution during crises",
                "icon": "🚨",
                "color": "#f59e0b",
                "goal_amount": 15000.0,
                "owner_id": user_id
            }
        ]
        
        for project_data in projects_data:
            project = ProjectDB(**project_data)
            db.add(project)
        
        db.commit()
        print(f"✓ {len(projects_data)} sample projects created successfully")
        
    except Exception as e:
        print(f"✗ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

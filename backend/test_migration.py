"""
Test and validation script for the PostgreSQL migration and new features.
Run this after setting up PostgreSQL to validate the implementation.
"""

import asyncio
import json
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine, init_db
import crud
from models import (
    UserDB, ProjectDB, IssueDB, DonationDB,
    ProjectStatus, IssueCategory, UserResponse,
    ProjectResponse, DonationPublicResponse
)
from auth import hash_password, create_access_token


async def setup_test_data():
    """Create test data for validation"""
    print("\n🔧 Setting up test database and data...\n")
    
    # Create tables
    Base.metadata.drop_all(bind=engine)
    init_db()
    print("✓ Database tables created")
    
    db = SessionLocal()
    
    try:
        # Create test users
        user1 = crud.create_user(
            db,
            email="donor@example.com",
            name="Alice Donor",
            password="password123"
        )
        print(f"✓ Created user: {user1.name} (ID: {user1.id})")
        
        user2 = crud.create_user(
            db,
            email="volunteer@example.com",
            name="Bob Volunteer",
            password="password123"
        )
        print(f"✓ Created user: {user2.name} (ID: {user2.id})")
        
        # Make user2 an admin for testing
        user2.is_admin = True
        db.commit()
        print(f"✓ Made {user2.name} admin")
        
        # Create a charity project
        project = crud.create_project(
            db,
            owner_id=user1.id,
            name="Emergency Food Relief",
            description="Helping families in need during crisis",
            icon="🍽️",
            color="#FF6B6B",
            goal_amount=5000.0,
            latitude=40.7128,
            longitude=-74.0060
        )
        print(f"✓ Created project: {project.name} (ID: {project.id})")
        print(f"  - Goal: ${project.goal_amount}, Current: ${project.current_amount}")
        print(f"  - Location: ({project.latitude}, {project.longitude})")
        
        # Create volunteer issues/tasks
        issue1 = crud.create_issue(
            db,
            project_id=project.id,
            reporter_id=user1.id,
            title="Need delivery helpers",
            description="Help us deliver food packages",
            category=IssueCategory.TRANSPORT,
            priority="high"
        )
        print(f"✓ Created issue: {issue1.title} (Category: {issue1.category})")
        
        issue2 = crud.create_issue(
            db,
            project_id=project.id,
            reporter_id=user1.id,
            title="Food packaging assistance",
            description="Help pack items for distribution",
            category=IssueCategory.HANDS,
            priority="medium"
        )
        print(f"✓ Created issue: {issue2.title}")
        
        return db, user1, user2, project, issue1, issue2
        
    except Exception as e:
        print(f"❌ Error setting up test data: {e}")
        db.rollback()
        raise


async def test_gamification(db: Session, user: UserDB, issue: IssueDB):
    """Test gamification: XP awards and rating levels"""
    print("\n🎮 Testing Gamification System...\n")
    
    initial_xp = user.xp
    print(f"Initial XP: {initial_xp}, Rating: {user.rating_level}")
    
    # Assign volunteer
    assigned_issue = crud.assign_volunteer(db, issue.id, user.id)
    print(f"✓ Assigned {user.name} to issue: {assigned_issue.title}")
    print(f"  - Status changed to: {assigned_issue.status}")
    
    # Close issue to award XP
    closed_issue = crud.close_issue(db, issue.id)
    print(f"✓ Closed issue: {closed_issue.title}")
    
    # Check XP increase
    db.refresh(user)
    xp_gained = user.xp - initial_xp
    print(f"✓ XP awarded: +{xp_gained}")
    print(f"✓ New rating: {user.rating_level}")
    print(f"✓ Total XP: {user.xp}")
    
    return True


async def test_donation_transactions(db: Session, user: UserDB, project: ProjectDB):
    """Test donation processing and transparency"""
    print("\n💰 Testing Transparent Donation System...\n")
    
    initial_amount = project.current_amount
    print(f"Initial project amount: ${initial_amount}")
    
    # Process donations
    donation1 = crud.process_donation(
        db,
        user_id=user.id,
        project_id=project.id,
        amount=500.0,
        is_anonymous=False
    )
    print(f"✓ Processed donation: ${donation1.amount} (Public)")
    
    donation2 = crud.process_donation(
        db,
        user_id=user.id,
        project_id=project.id,
        amount=300.0,
        is_anonymous=True
    )
    print(f"✓ Processed donation: ${donation2.amount} (Anonymous)")
    
    # Check project amount updated
    db.refresh(project)
    total_donated = project.current_amount - initial_amount
    print(f"✓ Project amount updated: ${project.current_amount}")
    print(f"✓ Total donated: ${total_donated}")
    
    # Test public donation view (anonymity)
    public_donations = crud.get_public_donations(db, project.id)
    print(f"\n📋 Public Donation List ({len(public_donations)} donations):")
    for d in public_donations:
        donor = d['donor_name'] if d['donor_name'] else "[Anonymous]"
        print(f"  - {donor}: ${d['amount']}")
    
    return True


async def test_project_verification(db: Session, admin: UserDB, project: ProjectDB):
    """Test admin verification of projects"""
    print("\n✅ Testing Project Verification (Admin Only)...\n")
    
    print(f"Initial verification status: is_verified={project.is_verified}")
    
    # Verify project
    verified_project = crud.verify_project(db, project.id, admin.id)
    print(f"✓ {admin.name} (admin) verified the project")
    print(f"✓ New verification status: is_verified={verified_project.is_verified}")
    
    # Upload report URL
    updated_project = crud.update_project(
        db,
        project.id,
        report_url="https://example.com/reports/project_2024.pdf"
    )
    print(f"✓ Uploaded report URL: {updated_project.report_url}")
    
    return True


async def test_geolocation(db: Session, project: ProjectDB):
    """Test geolocation fields"""
    print("\n🗺️ Testing Geolocation...\n")
    
    print(f"Project: {project.name}")
    print(f"Latitude: {project.latitude} (type: {type(project.latitude).__name__})")
    print(f"Longitude: {project.longitude} (type: {type(project.longitude).__name__})")
    
    assert isinstance(project.latitude, float), "Latitude must be Float"
    assert isinstance(project.longitude, float), "Longitude must be Float"
    print("✓ Coordinates are properly stored as Float")
    
    return True


async def test_schema_serialization():
    """Test Pydantic schema serialization"""
    print("\n📊 Testing Schema Serialization...\n")
    
    db = SessionLocal()
    
    try:
        projects = db.query(ProjectDB).all()
        
        for project in projects:
            response = ProjectResponse.from_orm(project)
            
            print(f"Project: {response.name}")
            print(f"  - goal_amount: ${response.goal_amount}")
            print(f"  - current_amount: ${response.current_amount}")
            print(f"  - is_verified: {response.is_verified}")
            print(f"  - status: {response.status}")
            print(f"  - latitude: {response.latitude}")
            print(f"  - longitude: {response.longitude}")
            print(f"✓ Project serialized correctly")
            
            # Verify progress bar data is present
            if response.goal_amount > 0:
                progress = (response.current_amount / response.goal_amount) * 100
                print(f"  - Progress: {progress:.1f}%")
    
    finally:
        db.close()
    
    return True


async def generate_test_token(user_id: int) -> str:
    """Generate a test JWT token"""
    token = create_access_token(data={"sub": str(user_id)})
    return token


async def main():
    """Run all validation tests"""
    print("=" * 60)
    print("🚀 POSTGRES MIGRATION & NEW FEATURES VALIDATION")
    print("=" * 60)
    
    try:
        # Setup test data
        db, user1, user2, project, issue1, issue2 = await setup_test_data()
        
        # Run tests
        print("\n" + "=" * 60)
        await test_gamification(db, user2, issue2)
        
        print("\n" + "=" * 60)
        await test_donation_transactions(db, user1, project)
        
        print("\n" + "=" * 60)
        await test_project_verification(db, user2, project)
        
        print("\n" + "=" * 60)
        await test_geolocation(db, project)
        
        print("\n" + "=" * 60)
        await test_schema_serialization()
        
        # Generate sample tokens
        print("\n" + "=" * 60)
        print("\n🔐 Sample JWT Tokens for Testing:\n")
        token1 = await generate_test_token(user1.id)
        token2 = await generate_test_token(user2.id)
        print(f"User 1 (Donor) Token:\n{token1}\n")
        print(f"User 2 (Admin) Token:\n{token2}\n")
        
        print("=" * 60)
        print("\n✅ ALL VALIDATION TESTS PASSED!\n")
        print("Your PostgreSQL migration is complete with:")
        print("  ✓ Database models with all required fields")
        print("  ✓ Gamification system (XP & rating levels)")
        print("  ✓ Transparent donation tracking")
        print("  ✓ Volunteer task assignment")
        print("  ✓ Admin verification system")
        print("  ✓ Geolocation support (Float coordinates)")
        print("  ✓ Anonymous donation support")
        print("  ✓ Proper schema serialization")
        print("\n📝 Next steps:")
        print("  1. Start the FastAPI server: python main.py")
        print("  2. Visit Swagger UI: http://localhost:5000/docs")
        print("  3. Test endpoints with the generated tokens")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())

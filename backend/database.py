from datetime import datetime, timedelta
from auth import hash_password

# In-memory databases
users_db = {}
projects_db = {}
issues_db = {}
notifications_db = {}


def init_database():
    """Initialize database with mock data"""
    
    # Create mock users
    users = [
        {
            "id": "user-1",
            "name": "John Donor",
            "email": "donor@example.com",
            "password": hash_password("password123"),
            "role": "Donor",
            "avatar": "🥗",
            "joinedAt": datetime.now().isoformat()
        },
        {
            "id": "user-2",
            "name": "Jane Deliverer",
            "email": "deliverer@example.com",
            "password": hash_password("password123"),
            "role": "Deliverer",
            "avatar": "🚚",
            "joinedAt": datetime.now().isoformat()
        },
        {
            "id": "user-3",
            "name": "Bob Receiver",
            "email": "receiver@example.com",
            "password": hash_password("password123"),
            "role": "Receiver",
            "avatar": "🍱",
            "joinedAt": datetime.now().isoformat()
        }
    ]
    
    for user in users:
        users_db[user["id"]] = user
    
    
    # Create mock projects
    projects = [
        {
            "id": "proj-001",
            "name": "Downtown Food Drive",
            "description": "Collecting and distributing food items to homeless shelters downtown",
            "createdBy": "user-1",
            "members": ["user-1", "user-2"],
            "status": "active",
            "createdAt": (datetime.now() - timedelta(days=30)).isoformat()
        },
        {
            "id": "proj-002",
            "name": "Community Kitchen Initiative",
            "description": "Building community kitchens in underserved neighborhoods",
            "createdBy": "user-1",
            "members": ["user-1", "user-3"],
            "status": "active",
            "createdAt": (datetime.now() - timedelta(days=15)).isoformat()
        },
        {
            "id": "proj-003",
            "name": "School Lunch Program",
            "description": "Providing nutritious meals to school children",
            "createdBy": "user-2",
            "members": ["user-2", "user-3"],
            "status": "active",
            "createdAt": (datetime.now() - timedelta(days=7)).isoformat()
        }
    ]
    
    for project in projects:
        projects_db[project["id"]] = project
    
    
    # Create mock issues
    issues = [
        {
            "id": "issue-001",
            "title": "Need more volunteers",
            "description": "We need additional volunteers for weekend deliveries",
            "projectId": "proj-001",
            "createdBy": "user-1",
            "assignedTo": "user-2",
            "status": "open",
            "priority": "high",
            "createdAt": (datetime.now() - timedelta(days=5)).isoformat()
        },
        {
            "id": "issue-002",
            "title": "Purchase kitchen equipment",
            "description": "Need to buy ovens and stoves for community kitchen",
            "projectId": "proj-002",
            "createdBy": "user-1",
            "assignedTo": "user-1",
            "status": "in-progress",
            "priority": "high",
            "createdAt": (datetime.now() - timedelta(days=3)).isoformat()
        },
        {
            "id": "issue-003",
            "title": "Prepare meal plans",
            "description": "Create nutritious meal plans for next month",
            "projectId": "proj-003",
            "createdBy": "user-2",
            "assignedTo": None,
            "status": "open",
            "priority": "medium",
            "createdAt": datetime.now().isoformat()
        }
    ]
    
    for issue in issues:
        issues_db[issue["id"]] = issue
    
    
    # Create mock notifications
    notifications = [
        {
            "id": "notif-001",
            "userId": "user-1",
            "title": "New project member",
            "message": "Jane Deliverer joined Downtown Food Drive",
            "type": "info",
            "isRead": True,
            "createdAt": (datetime.now() - timedelta(days=2)).isoformat()
        },
        {
            "id": "notif-002",
            "userId": "user-2",
            "title": "Issue assigned to you",
            "message": "John Donor assigned you 'Need more volunteers'",
            "type": "info",
            "isRead": False,
            "createdAt": (datetime.now() - timedelta(hours=6)).isoformat()
        },
        {
            "id": "notif-003",
            "userId": "user-3",
            "title": "Welcome to Save Food",
            "message": "You've been added to Community Kitchen Initiative",
            "type": "welcome",
            "isRead": True,
            "createdAt": (datetime.now() - timedelta(days=1)).isoformat()
        }
    ]
    
    for notification in notifications:
        notifications_db[notification["id"]] = notification


# Initialize database on import
init_database()

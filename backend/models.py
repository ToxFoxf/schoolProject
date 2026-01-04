from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ============ User Models ============

class UserBase(BaseModel):
    name: str
    email: str
    role: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    avatar: Optional[str] = None
    joinedAt: Optional[datetime] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    avatar: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    password: Optional[str] = None

class AuthResponse(BaseModel):
    token: str
    user: UserResponse

class LoginRequest(BaseModel):
    email: str
    password: str

# ============ Project Models ============

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    icon: Optional[str] = "📦"
    color: Optional[str] = "#5e6ad2"

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None

class Project(BaseModel):
    id: str
    name: str
    description: str
    owner: str
    icon: str
    color: str
    members: List[str]
    createdAt: datetime
    updatedAt: datetime

# ============ Issue Models ============

class IssueCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    projectId: str
    priority: Optional[str] = "Medium"
    labels: Optional[List[str]] = []

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee: Optional[str] = None
    labels: Optional[List[str]] = None
    dueDate: Optional[datetime] = None

class IssueStatusUpdate(BaseModel):
    status: str

class Issue(BaseModel):
    id: str
    title: str
    description: str
    projectId: str
    status: str
    priority: str
    assignee: Optional[str] = None
    reporter: str
    labels: List[str]
    createdAt: datetime
    updatedAt: datetime
    dueDate: Optional[datetime] = None

# ============ Notification Models ============

class NotificationCreate(BaseModel):
    title: str
    message: str
    type: str  # 'donation', 'delivery', 'system'

class NotificationUpdate(BaseModel):
    read: bool

class Notification(BaseModel):
    id: str
    userId: str
    title: str
    message: str
    type: str
    read: bool
    createdAt: datetime

# ============ Error Response Models ============

class ErrorResponse(BaseModel):
    error: str

class MessageResponse(BaseModel):
    message: str

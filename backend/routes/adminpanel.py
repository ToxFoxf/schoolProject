from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Optional
from pydantic import BaseModel
from models import UserInDB
from auth import get_current_user_from_token
from database import users_db

router = APIRouter(prefix="/api/admin", tags=["adminpanel"])

class AdminUserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    isActive: bool

def get_admin_user_from_token(authorization: Optional[str] = Header(None)):
    """Extract and verify admin user from authorization header"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided"
        )
    
    try:
        token = authorization.split(" ")[1]
        user: UserInDB = get_current_user_from_token(token)
        if not user or user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        return user
    except (IndexError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )

@router.get("/users", response_model=list[AdminUserResponse])
async def get_all_users(authorization: Optional[str] = Header(None)):
    """Get all users (admin only)"""
    user = get_admin_user_from_token(authorization)
    
    return [AdminUserResponse(**user) for user in users_db.values()]

@router.put("/users/{user_id}/deactivate", response_model=dict)
async def deactivate_user(user_id: str, authorization: Optional[str] = Header(None)):
    """Deactivate a user (admin only)"""
    get_admin_user_from_token(authorization)
    
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    users_db[user_id]["isActive"] = False
    return {"message": f"User {user_id} deactivated successfully"}

@router.put("/users/{user_id}/activate", response_model=dict)
async def activate_user(user_id: str, authorization: Optional[str] = Header(None)):
    """Activate a user (admin only)"""
    get_admin_user_from_token(authorization)
    
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    users_db[user_id]["isActive"] = True
    return {"message": f"User {user_id} activated successfully"}

@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: str, authorization: Optional[str] = Header(None)):
    """Delete a user (admin only)"""
    get_admin_user_from_token(authorization)
    
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    del users_db[user_id]
    return {"message": f"User {user_id} deleted successfully"}

@router.get("/stats", response_model=dict)
async def get_system_stats(authorization: Optional[str] = Header(None)):
    """Get system statistics (admin only)"""
    user = get_admin_user_from_token(authorization)
    
    total_users = len(users_db)
    active_users = sum(1 for user in users_db.values() if user.get("isActive", True))
    
    return {
        "totalUsers": total_users,
        "activeUsers": active_users
    }

@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user_by_id(user_id: str, authorization: Optional[str] = Header(None)):
    """Get user by ID (admin only)"""
    get_admin_user_from_token(authorization)
    
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return AdminUserResponse(**users_db[user_id])

@router.put("/users/{user_id}/role", response_model=dict)
async def update_user_role(user_id: str, new_role: str, authorization: Optional[str] = Header(None)):
    """Update user role (admin only)"""
    get_admin_user_from_token(authorization)
    
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    users_db[user_id]["role"] = new_role
    return {"message": f"User {user_id} role updated to {new_role} successfully"}
    
from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional
from auth import verify_token, is_admin
from database import users_db

router = APIRouter(prefix="/api/users", tags=["users"])


def get_user_from_token(authorization: Optional[str] = Header(None)):
    """Extract and verify user from authorization header"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided"
        )
    
    try:
        token = authorization.split(" ")[1]
        payload = verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token"
            )
        return payload.get("userId")
    except (IndexError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )


@router.get("/me", response_model=dict)
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user profile"""
    user_id = get_user_from_token(authorization)
    user = users_db.get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "avatar": user["avatar"],
        "joinedAt": user.get("joinedAt")
    }


@router.get("/{user_id}", response_model=dict)
async def get_user(user_id: str, authorization: Optional[str] = Header(None)):
    """Get user by ID"""
    current_user_id = get_user_from_token(authorization)
    
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "avatar": user["avatar"]
    }


@router.put("/{user_id}", response_model=dict)
async def update_user(user_id: str, updates: UserUpdate, authorization: Optional[str] = Header(None)):
    """Update user profile"""
    current_user_id = get_user_from_token(authorization)
    
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if updates.name:
        user["name"] = updates.name
    if updates.avatar is not None:
        user["avatar"] = updates.avatar
    if updates.password:
        from auth import hash_password
        user["password"] = hash_password(updates.password)
    
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "avatar": user["avatar"]
    }


@router.get("", response_model=list)
async def get_all_users(authorization: Optional[str] = Header(None)):
    """Get all users (for team features)"""
    current_user_id = get_user_from_token(authorization)
    
    if not is_admin(users_db.get(current_user_id)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access denied"
        )
    
    users = []
    for user in users_db.values():
        users.append({
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "avatar": user["avatar"]
        })
    
    return users

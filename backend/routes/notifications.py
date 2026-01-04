from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional
from datetime import datetime
from uuid import uuid4
from auth import verify_token
from database import notifications_db
from models import NotificationCreate, NotificationUpdate

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


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


@router.get("", response_model=list)
async def get_notifications(authorization: Optional[str] = Header(None)):
    """Get all notifications for current user"""
    user_id = get_user_from_token(authorization)
    
    user_notifications = []
    for notification in notifications_db.values():
        if notification["userId"] == user_id:
            user_notifications.append({
                "id": notification["id"],
                "userId": notification["userId"],
                "title": notification["title"],
                "message": notification["message"],
                "type": notification["type"],
                "isRead": notification["isRead"],
                "createdAt": notification["createdAt"]
            })
    
    return user_notifications


@router.post("", response_model=dict)
async def create_notification(notification: NotificationCreate, authorization: Optional[str] = Header(None)):
    """Create a notification (internal use)"""
    get_user_from_token(authorization)
    
    notification_id = f"notif-{uuid4().hex[:8]}"
    new_notification = {
        "id": notification_id,
        "userId": notification.userId,
        "title": notification.title,
        "message": notification.message or "",
        "type": notification.type or "info",
        "isRead": False,
        "createdAt": datetime.now().isoformat()
    }
    
    notifications_db[notification_id] = new_notification
    
    return new_notification


@router.get("/unread-count", response_model=dict)
async def get_unread_count(authorization: Optional[str] = Header(None)):
    """Get count of unread notifications"""
    user_id = get_user_from_token(authorization)
    
    unread_count = 0
    for notification in notifications_db.values():
        if notification["userId"] == user_id and not notification["isRead"]:
            unread_count += 1
    
    return {"userId": user_id, "unreadCount": unread_count}


@router.get("/{notification_id}", response_model=dict)
async def get_notification(notification_id: str, authorization: Optional[str] = Header(None)):
    """Get notification details"""
    user_id = get_user_from_token(authorization)
    
    notification = notifications_db.get(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Can only view own notifications
    if notification["userId"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this notification"
        )
    
    return notification


@router.put("/{notification_id}", response_model=dict)
async def update_notification(notification_id: str, updates: NotificationUpdate, authorization: Optional[str] = Header(None)):
    """Update notification (mark as read, etc)"""
    user_id = get_user_from_token(authorization)
    
    notification = notifications_db.get(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Can only update own notifications
    if notification["userId"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this notification"
        )
    
    if updates.isRead is not None:
        notification["isRead"] = updates.isRead
    
    return notification


@router.delete("/{notification_id}", response_model=dict)
async def delete_notification(notification_id: str, authorization: Optional[str] = Header(None)):
    """Delete notification"""
    user_id = get_user_from_token(authorization)
    
    notification = notifications_db.get(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Can only delete own notifications
    if notification["userId"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this notification"
        )
    
    del notifications_db[notification_id]
    
    return {"message": f"Notification {notification_id} deleted"}


@router.post("/mark-all-read", response_model=dict)
async def mark_all_read(authorization: Optional[str] = Header(None)):
    """Mark all notifications as read"""
    user_id = get_user_from_token(authorization)
    
    count = 0
    for notification in notifications_db.values():
        if notification["userId"] == user_id:
            notification["isRead"] = True
            count += 1
    
    return {"message": f"Marked {count} notifications as read"}

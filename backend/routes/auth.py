from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Optional
# Если возникнет ошибка импорта, используй: from ..auth import verify_token
from auth import verify_token 
from database import users_db

router = APIRouter(prefix="/api/users", tags=["users"])

def get_current_user_id(authorization: Optional[str] = Header(None)):
    """Вспомогательная функция для извлечения ID пользователя"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided"
        )
    
    try:
        # Убираем 'Bearer ' и берем сам токен
        token = authorization.split(" ")[1]
        payload = verify_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token"
            )
        
        # Важно: убедись, что при создании токена ты записываешь именно 'userId'
        return payload.get("userId")
    except (IndexError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )

@router.get("/me", response_model=dict)
async def get_my_profile(user_id: str = Depends(get_current_user_id)):
    """Получить профиль текущего пользователя через Depends"""
    user = users_db.get(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.get("/{user_id}", response_model=dict)
async def get_user_by_id(user_id: str, current_user_id: str = Depends(get_current_user_id)):  
    """Получить пользователя по ID (с проверкой прав)"""
    # Проверка: пользователь может смотреть только свой профиль
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

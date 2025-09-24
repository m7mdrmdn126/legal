from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
from models.auth import LoginRequest, LoginResponse
from models.user import User
from utils.auth import auth_utils
from config.database import db_manager
from config.settings import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """User login endpoint"""
    
    # Get user from database
    users = db_manager.execute_query(
        "SELECT * FROM users WHERE username = ? AND is_active = 1",
        (login_data.username,)
    )
    
    if not users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="اسم المستخدم أو كلمة المرور غير صحيحة"
        )
    
    user_data = users[0]
    
    # Verify password
    if not auth_utils.verify_password(login_data.password, user_data['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="اسم المستخدم أو كلمة المرور غير صحيحة"
        )
    
    # Create access token
    token_data = {
        "user_id": user_data['id'],
        "username": user_data['username'],
        "user_type": user_data['user_type']
    }
    
    access_token = auth_utils.create_access_token(token_data)
    expires_in = settings.access_token_expire_hours * 3600  # Convert to seconds
    
    # Create user response (without password hash)
    user_response = User(
        id=user_data['id'],
        username=user_data['username'],
        full_name=user_data['full_name'],
        user_type=user_data['user_type'],
        is_active=user_data['is_active'],
        created_at=user_data['created_at'],
        updated_at=user_data['updated_at']
    )
    
    return LoginResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=user_response
    )

@router.post("/logout")
async def logout():
    """User logout endpoint"""
    # In JWT, logout is handled client-side by removing the token
    # Server-side blacklisting can be implemented if needed
    return {"message": "تم تسجيل الخروج بنجاح"}

@router.post("/refresh")
async def refresh_token():
    """Refresh token endpoint - placeholder for future implementation"""
    # This would typically involve refresh tokens stored in database
    # For now, client should re-authenticate when token expires
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="تجديد الرمز المميز غير مدعوم حالياً"
    )

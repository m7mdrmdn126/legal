from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from models.user import User, UserCreate, UserUpdate, UserPasswordUpdate
from models.base import PaginatedResponse
from dependencies.auth import get_admin_user, get_current_user
from config.database import db_manager
from config.settings import settings
from utils.auth import auth_utils
from utils.database import db_utils

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=PaginatedResponse[User])
async def get_users(
    page: int = Query(1, ge=1),
    size: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    search: Optional[str] = Query(None),
    admin_user: User = Depends(get_admin_user)
):
    """Get all users (Admin only)"""
    
    base_query = """
    SELECT id, username, full_name, user_type, is_active, created_at, updated_at
    FROM users
    """
    
    params = []
    
    if search:
        search_condition, search_params = db_utils.build_search_conditions(
            search, ['username', 'full_name']
        )
        base_query += f" WHERE {search_condition}"
        params.extend(search_params)
    
    base_query += " ORDER BY created_at DESC"
    
    result = db_utils.paginate_query(base_query, tuple(params), page, size)
    
    return PaginatedResponse(**result)

@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    admin_user: User = Depends(get_admin_user)
):
    """Create new user (Admin only)"""
    
    # Check if username already exists
    existing_users = db_manager.execute_query(
        "SELECT id FROM users WHERE username = ?",
        (user_data.username,)
    )
    
    if existing_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="اسم المستخدم موجود بالفعل"
        )
    
    # Hash password
    password_hash = auth_utils.hash_password(user_data.password)
    
    # Create user
    user_id = db_manager.execute_write(
        """INSERT INTO users (username, password_hash, full_name, user_type, created_by, updated_by)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_data.username, password_hash, user_data.full_name, 
         user_data.user_type.value, admin_user.id, admin_user.id)
    )
    
    # Get created user
    users = db_manager.execute_query(
        "SELECT id, username, full_name, user_type, is_active, created_at, updated_at FROM users WHERE id = ?",
        (user_id,)
    )
    
    return User(**users[0])

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Get user by ID (Admin only)"""
    
    users = db_manager.execute_query(
        "SELECT id, username, full_name, user_type, is_active, created_at, updated_at FROM users WHERE id = ?",
        (user_id,)
    )
    
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    return User(**users[0])

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    admin_user: User = Depends(get_admin_user)
):
    """Update user (Admin only)"""
    
    # Check if user exists
    users = db_manager.execute_query("SELECT id FROM users WHERE id = ?", (user_id,))
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    # Build update query
    update_fields = []
    params = []
    
    if user_update.full_name is not None:
        update_fields.append("full_name = ?")
        params.append(user_update.full_name)
    
    if user_update.user_type is not None:
        update_fields.append("user_type = ?")
        params.append(user_update.user_type.value)
    
    if user_update.is_active is not None:
        update_fields.append("is_active = ?")
        params.append(1 if user_update.is_active else 0)
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لا يوجد بيانات للتحديث"
        )
    
    update_fields.append("updated_by = ?")
    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    params.extend([admin_user.id])
    
    # Update user
    query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
    params.append(user_id)
    
    db_manager.execute_write(query, tuple(params))
    
    # Return updated user
    updated_users = db_manager.execute_query(
        "SELECT id, username, full_name, user_type, is_active, created_at, updated_at FROM users WHERE id = ?",
        (user_id,)
    )
    
    return User(**updated_users[0])

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Delete user (Admin only)"""
    
    # Prevent admin from deleting themselves
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لا يمكن حذف حسابك الشخصي"
        )
    
    # Check if user exists
    users = db_manager.execute_query("SELECT id FROM users WHERE id = ?", (user_id,))
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    # Delete user (hard delete)
    rows_affected = db_manager.execute_write("DELETE FROM users WHERE id = ?", (user_id,))
    
    if rows_affected == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="فشل في حذف المستخدم"
        )
    
    return {"message": "تم حذف المستخدم بنجاح"}

@router.post("/{user_id}/activate")
async def activate_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Activate user (Admin only)"""
    
    rows_affected = db_manager.execute_write(
        "UPDATE users SET is_active = 1, updated_by = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (admin_user.id, user_id)
    )
    
    if rows_affected == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    # Return updated user data
    users = db_manager.execute_query(
        """SELECT id, username, full_name, user_type, is_active, 
           created_at, updated_at, created_by, updated_by 
           FROM users WHERE id = ?""",
        (user_id,)
    )
    
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    user_data = users[0]
    return {
        "id": user_data["id"],
        "username": user_data["username"],
        "full_name": user_data["full_name"],
        "user_type": user_data["user_type"],
        "is_active": bool(user_data["is_active"]),
        "created_at": user_data["created_at"],
        "updated_at": user_data["updated_at"],
        "created_by": user_data["created_by"],
        "updated_by": user_data["updated_by"]
    }

@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Deactivate user (Admin only)"""
    
    # Prevent admin from deactivating themselves
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لا يمكن إلغاء تفعيل حسابك الشخصي"
        )
    
    rows_affected = db_manager.execute_write(
        "UPDATE users SET is_active = 0, updated_by = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (admin_user.id, user_id)
    )
    
    if rows_affected == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    # Return updated user data
    users = db_manager.execute_query(
        """SELECT id, username, full_name, user_type, is_active, 
           created_at, updated_at, created_by, updated_by 
           FROM users WHERE id = ?""",
        (user_id,)
    )
    
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    user_data = users[0]
    return {
        "id": user_data["id"],
        "username": user_data["username"],
        "full_name": user_data["full_name"],
        "user_type": user_data["user_type"],
        "is_active": bool(user_data["is_active"]),
        "created_at": user_data["created_at"],
        "updated_at": user_data["updated_at"],
        "created_by": user_data["created_by"],
        "updated_by": user_data["updated_by"]
    }

@router.put("/{user_id}/password")
async def update_user_password(
    user_id: int,
    password_update: UserPasswordUpdate,
    admin_user: User = Depends(get_admin_user)
):
    """Update user password (Admin only)"""
    
    # Check if user exists
    users = db_manager.execute_query("SELECT id FROM users WHERE id = ?", (user_id,))
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المستخدم غير موجود"
        )
    
    # Hash new password
    password_hash = auth_utils.hash_password(password_update.new_password)
    
    # Update password
    db_manager.execute_write(
        "UPDATE users SET password_hash = ?, updated_by = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (password_hash, admin_user.id, user_id)
    )
    
    return {"message": "تم تحديث كلمة المرور بنجاح"}

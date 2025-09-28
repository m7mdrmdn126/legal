"""
Phone Directory API Routes
==========================

API endpoints for phone directory (دليل التليفونات) management.
Supports role-based access control:
- Admin: Full CRUD (Create, Read, Update, Delete)  
- User: CRU only (Create, Read, Update - no Delete)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from datetime import datetime

from models.phone_directory import (
    PhoneDirectoryCreate,
    PhoneDirectoryUpdate,
    PhoneDirectoryResponse,
    PhoneDirectoryListResponse,
    PhoneDirectorySearchRequest
)
from models.base import BaseResponse, PaginatedResponse
from models.user import User
from dependencies.auth import get_current_user
from config.database import db_manager

router = APIRouter(prefix="/phone-directory", tags=["Phone Directory"])

def is_admin(current_user: User) -> bool:
    """Check if current user is admin"""
    return current_user.user_type == "admin"

@router.post("/", response_model=PhoneDirectoryResponse)
async def create_phone_entry(
    entry: PhoneDirectoryCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new phone directory entry.
    Available to both admin and regular users.
    """
    
    try:
        # Insert new entry using db_manager
        entry_id = db_manager.execute_write("""
            INSERT INTO phone_directory (الاسم, الرقم, الجهه, created_by, updated_by)
            VALUES (?, ?, ?, ?, ?)
        """, (
            entry.الاسم,
            entry.الرقم, 
            entry.الجهه,
            current_user.id,
            current_user.id
        ))
        
        if not entry_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create entry"
            )
        
        # Fetch the created entry
        rows = db_manager.execute_query("""
            SELECT id, الاسم, الرقم, الجهه, created_at, updated_at, created_by, updated_by
            FROM phone_directory WHERE id = ?
        """, (entry_id,))
        
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created entry"
            )
        
        row = rows[0]
        return PhoneDirectoryResponse(
            id=row["id"],
            الاسم=row["الاسم"],
            الرقم=row["الرقم"], 
            الجهه=row["الجهه"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            created_by=row["created_by"],
            updated_by=row["updated_by"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating phone entry: {str(e)}"
        )

@router.get("/", response_model=PhoneDirectoryListResponse)
async def list_phone_entries(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in all fields"),
    name: Optional[str] = Query(None, alias="الاسم", description="Search by name"),
    phone: Optional[str] = Query(None, alias="الرقم", description="Search by phone"),
    org: Optional[str] = Query(None, alias="الجهه", description="Search by organization"),
    current_user: User = Depends(get_current_user)
):
    """
    List phone directory entries with optional search and pagination.
    Available to both admin and regular users.
    """
    
    try:
        # Build WHERE clause for search
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append("(الاسم LIKE ? OR الرقم LIKE ? OR الجهه LIKE ?)")
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        if name:
            where_conditions.append("الاسم LIKE ?")
            params.append(f"%{name}%")
            
        if phone:
            where_conditions.append("الرقم LIKE ?")
            params.append(f"%{phone}%")
            
        if org:
            where_conditions.append("الجهه LIKE ?")
            params.append(f"%{org}%")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Get total count
        count_rows = db_manager.execute_query(f"""
            SELECT COUNT(*) as total FROM phone_directory WHERE {where_clause}
        """, params)
        
        total = count_rows[0]["total"] if count_rows else 0
        
        # Calculate pagination
        offset = (page - 1) * size
        pages = (total + size - 1) // size
        
        # Get entries
        rows = db_manager.execute_query(f"""
            SELECT id, الاسم, الرقم, الجهه, created_at, updated_at, created_by, updated_by
            FROM phone_directory 
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, params + [size, offset])
        
        entries = []
        for row in rows:
            entries.append(PhoneDirectoryResponse(
                id=row["id"],
                الاسم=row["الاسم"],
                الرقم=row["الرقم"],
                الجهه=row["الجهه"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                created_by=row["created_by"],
                updated_by=row["updated_by"]
            ))
        
        return PhoneDirectoryListResponse(
            items=entries,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing phone entries: {str(e)}"
        )

@router.get("/{entry_id}", response_model=PhoneDirectoryResponse)
async def get_phone_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific phone directory entry by ID.
    Available to both admin and regular users.
    """
    
    try:
        rows = db_manager.execute_query("""
            SELECT id, الاسم, الرقم, الجهه, created_at, updated_at, created_by, updated_by
            FROM phone_directory WHERE id = ?
        """, (entry_id,))
        
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone entry not found"
            )
        
        row = rows[0]
        return PhoneDirectoryResponse(
            id=row["id"],
            الاسم=row["الاسم"],
            الرقم=row["الرقم"],
            الجهه=row["الجهه"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            created_by=row["created_by"],
            updated_by=row["updated_by"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting phone entry: {str(e)}"
        )

@router.put("/{entry_id}", response_model=PhoneDirectoryResponse)
async def update_phone_entry(
    entry_id: int,
    entry: PhoneDirectoryUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a phone directory entry.
    Available to both admin and regular users.
    """
    
    try:
        # Check if entry exists
        existing_rows = db_manager.execute_query(
            "SELECT id, created_by FROM phone_directory WHERE id = ?", 
            (entry_id,)
        )
        
        if not existing_rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone entry not found"
            )
        
        # Build update query dynamically for non-None fields
        update_fields = []
        params = []
        
        if entry.الاسم is not None:
            update_fields.append("الاسم = ?")
            params.append(entry.الاسم)
            
        if entry.الرقم is not None:
            update_fields.append("الرقم = ?")
            params.append(entry.الرقم)
            
        if entry.الجهه is not None:
            update_fields.append("الجهه = ?")
            params.append(entry.الجهه)
        
        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Add updated_by and updated_at
        update_fields.extend(["updated_by = ?", "updated_at = CURRENT_TIMESTAMP"])
        params.extend([current_user.id, entry_id])
        
        # Execute update
        db_manager.execute_write(f"""
            UPDATE phone_directory 
            SET {', '.join(update_fields)}
            WHERE id = ?
        """, params)
        
        # Fetch updated entry
        rows = db_manager.execute_query("""
            SELECT id, الاسم, الرقم, الجهه, created_at, updated_at, created_by, updated_by
            FROM phone_directory WHERE id = ?
        """, (entry_id,))
        
        if not rows:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve updated entry"
            )
        
        row = rows[0]
        return PhoneDirectoryResponse(
            id=row["id"],
            الاسم=row["الاسم"],
            الرقم=row["الرقم"],
            الجهه=row["الجهه"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            created_by=row["created_by"],
            updated_by=row["updated_by"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating phone entry: {str(e)}"
        )

@router.delete("/{entry_id}", response_model=BaseResponse)
async def delete_phone_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a phone directory entry.
    Available only to admin users.
    """
    
    # Check admin permission
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can delete phone directory entries"
        )
    
    try:
        # Check if entry exists
        existing_rows = db_manager.execute_query(
            "SELECT id FROM phone_directory WHERE id = ?", 
            (entry_id,)
        )
        
        if not existing_rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone entry not found"
            )
        
        # Delete entry
        rows_affected = db_manager.execute_write(
            "DELETE FROM phone_directory WHERE id = ?", 
            (entry_id,)
        )
        
        if rows_affected == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete entry"
            )
        
        return BaseResponse(
            success=True,
            message="Phone directory entry deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting phone entry: {str(e)}"
        )

@router.post("/search", response_model=PhoneDirectoryListResponse)
async def search_phone_entries(
    search_request: PhoneDirectorySearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Advanced search for phone directory entries.
    Available to both admin and regular users.
    """
    
    return await list_phone_entries(
        page=search_request.page,
        size=search_request.size,
        search=search_request.search_term,
        name=search_request.الاسم,
        phone=search_request.الرقم,
        org=search_request.الجهه,
        current_user=current_user
    )

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from models.case_session import CaseSession, CaseSessionCreate, CaseSessionUpdate
from models.base import PaginatedResponse
from dependencies.auth import get_current_user, get_admin_user
from models.user import User
from config.database import db_manager
from config.settings import settings
from utils.database import db_utils

router = APIRouter(tags=["Case Sessions"])

@router.get("/cases/{case_id}/sessions", response_model=PaginatedResponse[CaseSession])
async def get_case_sessions(
    case_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    current_user: User = Depends(get_current_user)
):
    """Get all sessions for a specific case"""
    
    # Check if case exists
    cases = db_manager.execute_query("SELECT id FROM cases WHERE id = ?", (case_id,))
    if not cases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="القضية غير موجودة"
        )
    
    base_query = """
    SELECT cs.*, 
           cu.full_name as created_by_name,
           uu.full_name as updated_by_name
    FROM case_sessions cs
    LEFT JOIN users cu ON cs.created_by = cu.id
    LEFT JOIN users uu ON cs.updated_by = uu.id
    WHERE cs.case_id = ?
    ORDER BY cs.session_date DESC, cs.created_at DESC
    """
    
    params = (case_id,)
    result = db_utils.paginate_query(base_query, params, page, size)
    
    # Transform results to include user info
    for item in result['items']:
        if item.get('created_by'):
            item['created_by'] = {"id": item['created_by'], "full_name": item.get('created_by_name')}
        if item.get('updated_by'):
            item['updated_by'] = {"id": item['updated_by'], "full_name": item.get('updated_by_name')}
        # Remove temporary fields
        item.pop('created_by_name', None)
        item.pop('updated_by_name', None)
    
    return PaginatedResponse(**result)

@router.post("/cases/{case_id}/sessions", response_model=CaseSession, status_code=status.HTTP_201_CREATED)
async def create_case_session(
    case_id: int,
    session_data: CaseSessionCreate,
    current_user: User = Depends(get_current_user)
):
    """Add new session to case"""
    
    # Check if case exists
    cases = db_manager.execute_query("SELECT id FROM cases WHERE id = ?", (case_id,))
    if not cases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="القضية غير موجودة"
        )
    
    # Create session
    session_id = db_manager.execute_write(
        """INSERT INTO case_sessions (case_id, session_date, session_notes, created_by, updated_by)
           VALUES (?, ?, ?, ?, ?)""",
        (case_id, session_data.session_date, session_data.session_notes,
         current_user.id, current_user.id)
    )
    
    # Get created session
    sessions = db_manager.execute_query(
        """SELECT cs.*, 
                  cu.full_name as created_by_name,
                  uu.full_name as updated_by_name
           FROM case_sessions cs
           LEFT JOIN users cu ON cs.created_by = cu.id
           LEFT JOIN users uu ON cs.updated_by = uu.id
           WHERE cs.id = ?""",
        (session_id,)
    )
    
    session = sessions[0]
    
    # Add user info
    if session.get('created_by'):
        session['created_by'] = {"id": session['created_by'], "full_name": session.get('created_by_name')}
    if session.get('updated_by'):
        session['updated_by'] = {"id": session['updated_by'], "full_name": session.get('updated_by_name')}
    
    # Clean up temporary fields
    session.pop('created_by_name', None)
    session.pop('updated_by_name', None)
    
    return CaseSession(**session)

@router.get("/sessions/{session_id}", response_model=CaseSession)
async def get_case_session(
    session_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get session by ID"""
    
    sessions = db_manager.execute_query(
        """SELECT cs.*, 
                  cu.full_name as created_by_name,
                  uu.full_name as updated_by_name
           FROM case_sessions cs
           LEFT JOIN users cu ON cs.created_by = cu.id
           LEFT JOIN users uu ON cs.updated_by = uu.id
           WHERE cs.id = ?""",
        (session_id,)
    )
    
    if not sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="جلسة القضية غير موجودة"
        )
    
    session = sessions[0]
    
    # Add user info
    if session.get('created_by'):
        session['created_by'] = {"id": session['created_by'], "full_name": session.get('created_by_name')}
    if session.get('updated_by'):
        session['updated_by'] = {"id": session['updated_by'], "full_name": session.get('updated_by_name')}
    
    # Clean up temporary fields
    session.pop('created_by_name', None)
    session.pop('updated_by_name', None)
    
    return CaseSession(**session)

@router.put("/sessions/{session_id}", response_model=CaseSession)
async def update_case_session(
    session_id: int,
    session_update: CaseSessionUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update case session"""
    
    # Check if session exists
    existing = db_manager.execute_query("SELECT id FROM case_sessions WHERE id = ?", (session_id,))
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="جلسة القضية غير موجودة"
        )
    
    # Build update query
    update_fields = []
    params = []
    
    if session_update.session_date is not None:
        update_fields.append("session_date = ?")
        params.append(session_update.session_date)
    
    if session_update.session_notes is not None:
        update_fields.append("session_notes = ?")
        params.append(session_update.session_notes)
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لا يوجد بيانات للتحديث"
        )
    
    update_fields.append("updated_by = ?")
    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    params.extend([current_user.id])
    
    # Update session
    query = f"UPDATE case_sessions SET {', '.join(update_fields)} WHERE id = ?"
    params.append(session_id)
    
    db_manager.execute_write(query, tuple(params))
    
    # Return updated session
    return await get_case_session(session_id, current_user)

@router.delete("/sessions/{session_id}")
async def delete_case_session(
    session_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Delete case session (Admin only)"""
    
    # Check if session exists
    existing = db_manager.execute_query("SELECT id FROM case_sessions WHERE id = ?", (session_id,))
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="جلسة القضية غير موجودة"
        )
    
    # Delete session (hard delete)
    rows_affected = db_manager.execute_write("DELETE FROM case_sessions WHERE id = ?", (session_id,))
    
    if rows_affected == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="فشل في حذف جلسة القضية"
        )
    
    return {"message": "تم حذف جلسة القضية بنجاح"}

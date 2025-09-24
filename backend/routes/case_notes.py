from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from models.case_note import CaseNote, CaseNoteCreate, CaseNoteUpdate
from models.base import PaginatedResponse
from dependencies.auth import get_current_user, get_admin_user
from models.user import User
from config.database import db_manager
from config.settings import settings
from utils.database import db_utils

router = APIRouter(tags=["Case Notes"])

@router.get("/cases/{case_id}/notes", response_model=PaginatedResponse[CaseNote])
async def get_case_notes(
    case_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get all notes for a specific case"""
    
    # Check if case exists
    cases = db_manager.execute_query("SELECT id FROM cases WHERE id = ?", (case_id,))
    if not cases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="القضية غير موجودة"
        )
    
    base_query = """
    SELECT cn.*, 
           cu.full_name as created_by_name,
           uu.full_name as updated_by_name
    FROM case_notes cn
    LEFT JOIN users cu ON cn.created_by = cu.id
    LEFT JOIN users uu ON cn.updated_by = uu.id
    WHERE cn.case_id = ?
    """
    
    params = [case_id]
    
    # Add search condition for note text
    if search:
        search_condition, search_params = db_utils.build_search_conditions(
            search, ['cn.note_text']
        )
        base_query += f" AND {search_condition}"
        params.extend(search_params)
    
    base_query += " ORDER BY cn.created_at DESC"
    
    result = db_utils.paginate_query(base_query, tuple(params), page, size)
    
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

@router.post("/cases/{case_id}/notes", response_model=CaseNote, status_code=status.HTTP_201_CREATED)
async def create_case_note(
    case_id: int,
    note_data: CaseNoteCreate,
    current_user: User = Depends(get_current_user)
):
    """Add new note to case"""
    
    # Check if case exists
    cases = db_manager.execute_query("SELECT id FROM cases WHERE id = ?", (case_id,))
    if not cases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="القضية غير موجودة"
        )
    
    # Create note
    note_id = db_manager.execute_write(
        """INSERT INTO case_notes (case_id, note_text, created_by, updated_by)
           VALUES (?, ?, ?, ?)""",
        (case_id, note_data.note_text, current_user.id, current_user.id)
    )
    
    # Get created note
    notes = db_manager.execute_query(
        """SELECT cn.*, 
                  cu.full_name as created_by_name,
                  uu.full_name as updated_by_name
           FROM case_notes cn
           LEFT JOIN users cu ON cn.created_by = cu.id
           LEFT JOIN users uu ON cn.updated_by = uu.id
           WHERE cn.id = ?""",
        (note_id,)
    )
    
    note = notes[0]
    
    # Add user info
    if note.get('created_by'):
        note['created_by'] = {"id": note['created_by'], "full_name": note.get('created_by_name')}
    if note.get('updated_by'):
        note['updated_by'] = {"id": note['updated_by'], "full_name": note.get('updated_by_name')}
    
    # Clean up temporary fields
    note.pop('created_by_name', None)
    note.pop('updated_by_name', None)
    
    return CaseNote(**note)

@router.get("/notes/{note_id}", response_model=CaseNote)
async def get_case_note(
    note_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get note by ID"""
    
    notes = db_manager.execute_query(
        """SELECT cn.*, 
                  cu.full_name as created_by_name,
                  uu.full_name as updated_by_name
           FROM case_notes cn
           LEFT JOIN users cu ON cn.created_by = cu.id
           LEFT JOIN users uu ON cn.updated_by = uu.id
           WHERE cn.id = ?""",
        (note_id,)
    )
    
    if not notes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ملاحظة القضية غير موجودة"
        )
    
    note = notes[0]
    
    # Add user info
    if note.get('created_by'):
        note['created_by'] = {"id": note['created_by'], "full_name": note.get('created_by_name')}
    if note.get('updated_by'):
        note['updated_by'] = {"id": note['updated_by'], "full_name": note.get('updated_by_name')}
    
    # Clean up temporary fields
    note.pop('created_by_name', None)
    note.pop('updated_by_name', None)
    
    return CaseNote(**note)

@router.put("/notes/{note_id}", response_model=CaseNote)
async def update_case_note(
    note_id: int,
    note_update: CaseNoteUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update case note"""
    
    # Check if note exists
    existing = db_manager.execute_query("SELECT id FROM case_notes WHERE id = ?", (note_id,))
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ملاحظة القضية غير موجودة"
        )
    
    # Build update query
    update_fields = []
    params = []
    
    if note_update.note_text is not None:
        update_fields.append("note_text = ?")
        params.append(note_update.note_text)
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لا يوجد بيانات للتحديث"
        )
    
    update_fields.append("updated_by = ?")
    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    params.extend([current_user.id])
    
    # Update note
    query = f"UPDATE case_notes SET {', '.join(update_fields)} WHERE id = ?"
    params.append(note_id)
    
    db_manager.execute_write(query, tuple(params))
    
    # Return updated note
    return await get_case_note(note_id, current_user)

@router.delete("/notes/{note_id}")
async def delete_case_note(
    note_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Delete case note (Admin only)"""
    
    # Check if note exists
    existing = db_manager.execute_query("SELECT id FROM case_notes WHERE id = ?", (note_id,))
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ملاحظة القضية غير موجودة"
        )
    
    # Delete note (hard delete)
    rows_affected = db_manager.execute_write("DELETE FROM case_notes WHERE id = ?", (note_id,))
    
    if rows_affected == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="فشل في حذف ملاحظة القضية"
        )
    
    return {"message": "تم حذف ملاحظة القضية بنجاح"}

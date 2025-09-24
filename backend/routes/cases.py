from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from models.case import Case, CaseCreate, CaseUpdate, CaseWithDetails, JudgmentType
from models.base import PaginatedResponse
from dependencies.auth import get_current_user, get_admin_user
from models.user import User
from config.database import db_manager
from config.settings import settings
from utils.database import db_utils

router = APIRouter(prefix="/cases", tags=["Cases"])

@router.get("", response_model=PaginatedResponse[Case])
async def get_cases(
    page: int = Query(1, ge=1),
    size: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    search: Optional[str] = Query(None),
    case_type_id: Optional[int] = Query(None),
    judgment_type: Optional[JudgmentType] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get all cases with filtering"""
    
    base_query = """
    SELECT c.*, 
           ct.name as case_type_name,
           ct.description as case_type_description,
           cu.full_name as created_by_name,
           uu.full_name as updated_by_name
    FROM cases c
    JOIN case_types ct ON c.case_type_id = ct.id
    LEFT JOIN users cu ON c.created_by = cu.id
    LEFT JOIN users uu ON c.updated_by = uu.id
    """
    
    conditions = []
    params = []
    
    # Add search condition
    if search:
        search_condition, search_params = db_utils.build_search_conditions(
            search, ['c.case_number', 'c.plaintiff', 'c.defendant']
        )
        conditions.append(search_condition)
        params.extend(search_params)
    
    # Add case type filter
    if case_type_id:
        conditions.append("c.case_type_id = ?")
        params.append(case_type_id)
    
    # Add judgment type filter
    if judgment_type:
        conditions.append("c.judgment_type = ?")
        params.append(judgment_type.value)
    
    # Add WHERE clause if we have conditions
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    
    base_query += " ORDER BY c.created_at DESC"
    
    result = db_utils.paginate_query(base_query, tuple(params), page, size)
    
    # Transform results to include case type and user info
    for item in result['items']:
        # Add case type info
        if item.get('case_type_name'):
            item['case_type'] = {
                "id": item['case_type_id'],
                "name": item['case_type_name'],
                "description": item.get('case_type_description')
            }
        
        # Add user info
        if item.get('created_by'):
            item['created_by'] = {"id": item['created_by'], "full_name": item.get('created_by_name')}
        if item.get('updated_by'):
            item['updated_by'] = {"id": item['updated_by'], "full_name": item.get('updated_by_name')}
        
        # Remove temporary fields
        item.pop('case_type_name', None)
        item.pop('case_type_description', None)
        item.pop('created_by_name', None)
        item.pop('updated_by_name', None)
    
    return PaginatedResponse(**result)

@router.post("", response_model=Case, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_data: CaseCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new case"""
    
    # Check if case number already exists
    existing = db_manager.execute_query(
        "SELECT id FROM cases WHERE case_number = ?",
        (case_data.case_number,)
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="رقم القضية موجود بالفعل"
        )
    
    # Check if case type exists
    case_types = db_manager.execute_query(
        "SELECT id FROM case_types WHERE id = ?",
        (case_data.case_type_id,)
    )
    
    if not case_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="نوع القضية غير موجود"
        )
    
    # Check previous judgment reference if provided
    if case_data.previous_judgment_id:
        previous_cases = db_manager.execute_query(
            "SELECT id FROM cases WHERE id = ?",
            (case_data.previous_judgment_id,)
        )
        if not previous_cases:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="القضية المرجعية غير موجودة"
            )
    
    # Create case
    case_id = db_manager.execute_write(
        """INSERT INTO cases (case_number, plaintiff, defendant, case_type_id, 
                             judgment_type, previous_judgment_id, created_by, updated_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (case_data.case_number, case_data.plaintiff, case_data.defendant,
         case_data.case_type_id, case_data.judgment_type.value,
         case_data.previous_judgment_id, current_user.id, current_user.id)
    )
    
    # Get created case with related data
    cases = db_manager.execute_query(
        """SELECT c.*, 
                  ct.name as case_type_name,
                  ct.description as case_type_description,
                  cu.full_name as created_by_name,
                  uu.full_name as updated_by_name
           FROM cases c
           JOIN case_types ct ON c.case_type_id = ct.id
           LEFT JOIN users cu ON c.created_by = cu.id
           LEFT JOIN users uu ON c.updated_by = uu.id
           WHERE c.id = ?""",
        (case_id,)
    )
    
    case = cases[0]
    
    # Add case type info
    case['case_type'] = {
        "id": case['case_type_id'],
        "name": case['case_type_name'],
        "description": case.get('case_type_description')
    }
    
    # Add user info
    if case.get('created_by'):
        case['created_by'] = {"id": case['created_by'], "full_name": case.get('created_by_name')}
    if case.get('updated_by'):
        case['updated_by'] = {"id": case['updated_by'], "full_name": case.get('updated_by_name')}
    
    # Clean up temporary fields
    case.pop('case_type_name', None)
    case.pop('case_type_description', None)
    case.pop('created_by_name', None)
    case.pop('updated_by_name', None)
    
    return Case(**case)

@router.get("/{case_id}", response_model=Case)
async def get_case(
    case_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get case by ID"""
    
    cases = db_manager.execute_query(
        """SELECT c.*, 
                  ct.name as case_type_name,
                  ct.description as case_type_description,
                  cu.full_name as created_by_name,
                  uu.full_name as updated_by_name
           FROM cases c
           JOIN case_types ct ON c.case_type_id = ct.id
           LEFT JOIN users cu ON c.created_by = cu.id
           LEFT JOIN users uu ON c.updated_by = uu.id
           WHERE c.id = ?""",
        (case_id,)
    )
    
    if not cases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="القضية غير موجودة"
        )
    
    case = cases[0]
    
    # Add case type info
    case['case_type'] = {
        "id": case['case_type_id'],
        "name": case['case_type_name'],
        "description": case.get('case_type_description')
    }
    
    # Add user info
    if case.get('created_by'):
        case['created_by'] = {"id": case['created_by'], "full_name": case.get('created_by_name')}
    if case.get('updated_by'):
        case['updated_by'] = {"id": case['updated_by'], "full_name": case.get('updated_by_name')}
    
    # Clean up temporary fields
    case.pop('case_type_name', None)
    case.pop('case_type_description', None)
    case.pop('created_by_name', None)
    case.pop('updated_by_name', None)
    
    return Case(**case)

@router.get("/{case_id}/full", response_model=CaseWithDetails)
async def get_case_with_details(
    case_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get case with all related data (sessions, notes counts)"""
    
    # Get basic case data
    case_data = await get_case(case_id, current_user)
    
    # Get sessions count
    sessions_count = db_manager.execute_query(
        "SELECT COUNT(*) as count FROM case_sessions WHERE case_id = ?",
        (case_id,)
    )[0]['count']
    
    # Get notes count
    notes_count = db_manager.execute_query(
        "SELECT COUNT(*) as count FROM case_notes WHERE case_id = ?",
        (case_id,)
    )[0]['count']
    
    # Get latest session date
    latest_session = db_manager.execute_query(
        "SELECT session_date FROM case_sessions WHERE case_id = ? ORDER BY session_date DESC LIMIT 1",
        (case_id,)
    )
    
    latest_session_date = None
    if latest_session and latest_session[0]['session_date']:
        latest_session_date = latest_session[0]['session_date']
    
    # Convert Case to CaseWithDetails
    case_dict = case_data.dict()
    case_dict.update({
        "sessions_count": sessions_count,
        "notes_count": notes_count,
        "latest_session": latest_session_date
    })
    
    return CaseWithDetails(**case_dict)

@router.put("/{case_id}", response_model=Case)
async def update_case(
    case_id: int,
    case_update: CaseUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update case"""
    
    # Check if case exists
    existing = db_manager.execute_query("SELECT id FROM cases WHERE id = ?", (case_id,))
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="القضية غير موجودة"
        )
    
    # Check case number uniqueness if being updated
    if case_update.case_number:
        number_conflicts = db_manager.execute_query(
            "SELECT id FROM cases WHERE case_number = ? AND id != ?",
            (case_update.case_number, case_id)
        )
        if number_conflicts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="رقم القضية موجود بالفعل"
            )
    
    # Check case type exists if being updated
    if case_update.case_type_id:
        case_types = db_manager.execute_query(
            "SELECT id FROM case_types WHERE id = ?",
            (case_update.case_type_id,)
        )
        if not case_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="نوع القضية غير موجود"
            )
    
    # Check previous judgment reference if being updated
    if case_update.previous_judgment_id:
        previous_cases = db_manager.execute_query(
            "SELECT id FROM cases WHERE id = ?",
            (case_update.previous_judgment_id,)
        )
        if not previous_cases:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="القضية المرجعية غير موجودة"
            )
    
    # Build update query
    update_fields = []
    params = []
    
    if case_update.case_number is not None:
        update_fields.append("case_number = ?")
        params.append(case_update.case_number)
    
    if case_update.plaintiff is not None:
        update_fields.append("plaintiff = ?")
        params.append(case_update.plaintiff)
    
    if case_update.defendant is not None:
        update_fields.append("defendant = ?")
        params.append(case_update.defendant)
    
    if case_update.case_type_id is not None:
        update_fields.append("case_type_id = ?")
        params.append(case_update.case_type_id)
    
    if case_update.judgment_type is not None:
        update_fields.append("judgment_type = ?")
        params.append(case_update.judgment_type.value)
    
    if case_update.previous_judgment_id is not None:
        update_fields.append("previous_judgment_id = ?")
        params.append(case_update.previous_judgment_id)
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لا يوجد بيانات للتحديث"
        )
    
    update_fields.append("updated_by = ?")
    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    params.extend([current_user.id])
    
    # Update case
    query = f"UPDATE cases SET {', '.join(update_fields)} WHERE id = ?"
    params.append(case_id)
    
    db_manager.execute_write(query, tuple(params))
    
    # Return updated case
    return await get_case(case_id, current_user)

@router.delete("/{case_id}")
async def delete_case(
    case_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Delete case (Admin only)"""
    
    # Check if case exists
    existing = db_manager.execute_query("SELECT id FROM cases WHERE id = ?", (case_id,))
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="القضية غير موجودة"
        )
    
    # Delete case (CASCADE will handle related sessions and notes)
    rows_affected = db_manager.execute_write("DELETE FROM cases WHERE id = ?", (case_id,))
    
    if rows_affected == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="فشل في حذف القضية"
        )
    
    return {"message": "تم حذف القضية وجميع البيانات المتعلقة بها بنجاح"}

@router.get("/by-type/{case_type_id}", response_model=PaginatedResponse[Case])
async def get_cases_by_type(
    case_type_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    current_user: User = Depends(get_current_user)
):
    """Get cases by case type"""
    
    # Check if case type exists
    case_types = db_manager.execute_query(
        "SELECT id FROM case_types WHERE id = ?",
        (case_type_id,)
    )
    
    if not case_types:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="نوع القضية غير موجود"
        )
    
    return await get_cases(
        page=page,
        size=size,
        case_type_id=case_type_id,
        current_user=current_user
    )

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
from models.case_type import CaseType, CaseTypeCreate, CaseTypeUpdate
from models.base import PaginatedResponse
from dependencies.auth import get_current_user, get_admin_user
from models.user import User
from config.database import db_manager
from config.settings import settings
from utils.database import db_utils

router = APIRouter(prefix="/case-types", tags=["Case Types"])

@router.get("", response_model=PaginatedResponse[CaseType])
async def get_case_types(
    page: int = Query(1, ge=1),
    size: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get all case types"""
    
    base_query = """
    SELECT ct.*, 
           cu.full_name as created_by_name,
           uu.full_name as updated_by_name
    FROM case_types ct
    LEFT JOIN users cu ON ct.created_by = cu.id
    LEFT JOIN users uu ON ct.updated_by = uu.id
    """
    
    params = []
    
    if search:
        search_condition, search_params = db_utils.build_search_conditions(
            search, ['ct.name', 'ct.description']
        )
        base_query += f" WHERE {search_condition}"
        params.extend(search_params)
    
    base_query += " ORDER BY ct.name"
    
    result = db_utils.paginate_query(base_query, tuple(params), page, size)
    
    # Transform results to include user info
    for item in result['items']:
        if item.get('created_by'):
            item['created_by'] = {"id": item['created_by'], "full_name": item.get('created_by_name')}
        if item.get('updated_by'):
            item['updated_by'] = {"id": item['updated_by'], "full_name": item.get('updated_by_name')}
        # Remove the temporary name fields
        item.pop('created_by_name', None)
        item.pop('updated_by_name', None)
    
    return PaginatedResponse(**result)

@router.post("", response_model=CaseType, status_code=status.HTTP_201_CREATED)
async def create_case_type(
    case_type_data: CaseTypeCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new case type"""
    
    # Check if name already exists
    existing = db_manager.execute_query(
        "SELECT id FROM case_types WHERE LOWER(name) = LOWER(?)",
        (case_type_data.name,)
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="نوع القضية موجود بالفعل"
        )
    
    # Create case type
    case_type_id = db_manager.execute_write(
        """INSERT INTO case_types (name, description, created_by, updated_by)
           VALUES (?, ?, ?, ?)""",
        (case_type_data.name, case_type_data.description, current_user.id, current_user.id)
    )
    
    # Get created case type
    case_types = db_manager.execute_query(
        """SELECT ct.*, 
                  cu.full_name as created_by_name,
                  uu.full_name as updated_by_name
           FROM case_types ct
           LEFT JOIN users cu ON ct.created_by = cu.id
           LEFT JOIN users uu ON ct.updated_by = uu.id
           WHERE ct.id = ?""",
        (case_type_id,)
    )
    
    case_type = case_types[0]
    if case_type.get('created_by'):
        case_type['created_by'] = {"id": case_type['created_by'], "full_name": case_type.get('created_by_name')}
    if case_type.get('updated_by'):
        case_type['updated_by'] = {"id": case_type['updated_by'], "full_name": case_type.get('updated_by_name')}
    case_type.pop('created_by_name', None)
    case_type.pop('updated_by_name', None)
    
    return CaseType(**case_type)

@router.get("/{case_type_id}", response_model=CaseType)
async def get_case_type(
    case_type_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get case type by ID"""
    
    case_types = db_manager.execute_query(
        """SELECT ct.*, 
                  cu.full_name as created_by_name,
                  uu.full_name as updated_by_name
           FROM case_types ct
           LEFT JOIN users cu ON ct.created_by = cu.id
           LEFT JOIN users uu ON ct.updated_by = uu.id
           WHERE ct.id = ?""",
        (case_type_id,)
    )
    
    if not case_types:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="نوع القضية غير موجود"
        )
    
    case_type = case_types[0]
    if case_type.get('created_by'):
        case_type['created_by'] = {"id": case_type['created_by'], "full_name": case_type.get('created_by_name')}
    if case_type.get('updated_by'):
        case_type['updated_by'] = {"id": case_type['updated_by'], "full_name": case_type.get('updated_by_name')}
    case_type.pop('created_by_name', None)
    case_type.pop('updated_by_name', None)
    
    return CaseType(**case_type)

@router.put("/{case_type_id}", response_model=CaseType)
async def update_case_type(
    case_type_id: int,
    case_type_update: CaseTypeUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update case type"""
    
    # Check if case type exists
    existing = db_manager.execute_query("SELECT id FROM case_types WHERE id = ?", (case_type_id,))
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="نوع القضية غير موجود"
        )
    
    # Check if new name conflicts with existing (if name is being updated)
    if case_type_update.name:
        name_conflicts = db_manager.execute_query(
            "SELECT id FROM case_types WHERE LOWER(name) = LOWER(?) AND id != ?",
            (case_type_update.name, case_type_id)
        )
        if name_conflicts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="نوع القضية موجود بالفعل"
            )
    
    # Build update query
    update_fields = []
    params = []
    
    if case_type_update.name is not None:
        update_fields.append("name = ?")
        params.append(case_type_update.name)
    
    if case_type_update.description is not None:
        update_fields.append("description = ?")
        params.append(case_type_update.description)
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لا يوجد بيانات للتحديث"
        )
    
    update_fields.append("updated_by = ?")
    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    params.extend([current_user.id])
    
    # Update case type
    query = f"UPDATE case_types SET {', '.join(update_fields)} WHERE id = ?"
    params.append(case_type_id)
    
    db_manager.execute_write(query, tuple(params))
    
    # Return updated case type
    case_types = db_manager.execute_query(
        """SELECT ct.*, 
                  cu.full_name as created_by_name,
                  uu.full_name as updated_by_name
           FROM case_types ct
           LEFT JOIN users cu ON ct.created_by = cu.id
           LEFT JOIN users uu ON ct.updated_by = uu.id
           WHERE ct.id = ?""",
        (case_type_id,)
    )
    
    case_type = case_types[0]
    if case_type.get('created_by'):
        case_type['created_by'] = {"id": case_type['created_by'], "full_name": case_type.get('created_by_name')}
    if case_type.get('updated_by'):
        case_type['updated_by'] = {"id": case_type['updated_by'], "full_name": case_type.get('updated_by_name')}
    case_type.pop('created_by_name', None)
    case_type.pop('updated_by_name', None)
    
    return CaseType(**case_type)

@router.delete("/{case_type_id}")
async def delete_case_type(
    case_type_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Delete case type (Admin only)"""
    
    # Check if case type exists
    existing = db_manager.execute_query("SELECT id FROM case_types WHERE id = ?", (case_type_id,))
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="نوع القضية غير موجود"
        )
    
    # Check if case type is being used by any cases
    cases_using_type = db_manager.execute_query(
        "SELECT COUNT(*) as count FROM cases WHERE case_type_id = ?",
        (case_type_id,)
    )
    
    if cases_using_type[0]['count'] > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لا يمكن حذف نوع القضية لأنه مستخدم في قضايا موجودة"
        )
    
    # Delete case type (hard delete)
    rows_affected = db_manager.execute_write("DELETE FROM case_types WHERE id = ?", (case_type_id,))
    
    if rows_affected == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="فشل في حذف نوع القضية"
        )
    
    return {"message": "تم حذف نوع القضية بنجاح"}

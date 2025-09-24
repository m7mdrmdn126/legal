from fastapi import APIRouter, Depends
from typing import Dict, Any
from dependencies.auth import get_current_user
from models.user import User
from config.database import db_manager

router = APIRouter(prefix="/stats", tags=["Statistics"])

@router.get("/dashboard")
async def get_dashboard_statistics(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get dashboard statistics"""
    
    # Total counts
    total_cases = db_manager.execute_query("SELECT COUNT(*) as count FROM cases")[0]['count']
    total_users = db_manager.execute_query("SELECT COUNT(*) as count FROM users WHERE is_active = 1")[0]['count']
    total_case_types = db_manager.execute_query("SELECT COUNT(*) as count FROM case_types")[0]['count']
    total_sessions = db_manager.execute_query("SELECT COUNT(*) as count FROM case_sessions")[0]['count']
    total_notes = db_manager.execute_query("SELECT COUNT(*) as count FROM case_notes")[0]['count']
    
    # Cases by judgment type
    judgment_stats = db_manager.execute_query("""
        SELECT judgment_type, COUNT(*) as case_count
        FROM cases
        GROUP BY judgment_type
        ORDER BY case_count DESC
    """)
    
    # Cases by type
    type_stats = db_manager.execute_query("""
        SELECT ct.name, COUNT(c.id) as case_count
        FROM case_types ct
        LEFT JOIN cases c ON ct.id = c.case_type_id
        GROUP BY ct.id, ct.name
        ORDER BY case_count DESC
    """)
    
    # Recent cases (last 10)
    recent_cases = db_manager.execute_query("""
        SELECT c.id, c.case_number, c.plaintiff, c.defendant, 
               ct.name as case_type_name, c.judgment_type, c.created_at
        FROM cases c
        JOIN case_types ct ON c.case_type_id = ct.id
        ORDER BY c.created_at DESC
        LIMIT 10
    """)
    
    # Cases with upcoming sessions (if session_date is in the future)
    upcoming_sessions = db_manager.execute_query("""
        SELECT c.case_number, c.plaintiff, c.defendant,
               cs.session_date, cs.session_notes
        FROM case_sessions cs
        JOIN cases c ON cs.case_id = c.id
        WHERE cs.session_date > datetime('now')
        ORDER BY cs.session_date ASC
        LIMIT 10
    """)
    
    # Monthly case creation trend (last 6 months)
    monthly_trend = db_manager.execute_query("""
        SELECT strftime('%Y-%m', created_at) as month,
               COUNT(*) as count
        FROM cases
        WHERE created_at >= date('now', '-6 months')
        GROUP BY strftime('%Y-%m', created_at)
        ORDER BY month ASC
    """)
    
    return {
        "total_cases": total_cases,
        "total_users": total_users,
        "total_case_types": total_case_types,
        "total_sessions": total_sessions,
        "total_notes": total_notes,
        "cases_by_judgment": judgment_stats,
        "cases_by_type": type_stats,
        "recent_cases": recent_cases,
        "upcoming_sessions": upcoming_sessions,
        "monthly_trend": monthly_trend
    }

@router.get("/cases-by-type")
async def get_cases_by_type(
    current_user: User = Depends(get_current_user)
):
    """Get cases count by type"""
    
    result = db_manager.execute_query("""
        SELECT ct.id, ct.name, ct.description, COUNT(c.id) as case_count
        FROM case_types ct
        LEFT JOIN cases c ON ct.id = c.case_type_id
        GROUP BY ct.id, ct.name, ct.description
        ORDER BY case_count DESC, ct.name ASC
    """)
    
    return result

@router.get("/cases-by-judgment")
async def get_cases_by_judgment(
    current_user: User = Depends(get_current_user)
):
    """Get cases count by judgment type"""
    
    result = db_manager.execute_query("""
        SELECT judgment_type, COUNT(*) as case_count
        FROM cases
        GROUP BY judgment_type
        ORDER BY case_count DESC
    """)
    
    return result

@router.get("/user-activity")
async def get_user_activity(
    current_user: User = Depends(get_current_user)
):
    """Get user activity statistics"""
    
    # Cases created by user
    cases_by_user = db_manager.execute_query("""
        SELECT u.full_name, COUNT(c.id) as cases_created
        FROM users u
        LEFT JOIN cases c ON u.id = c.created_by
        WHERE u.is_active = 1
        GROUP BY u.id, u.full_name
        ORDER BY cases_created DESC
    """)
    
    # Sessions created by user
    sessions_by_user = db_manager.execute_query("""
        SELECT u.full_name, COUNT(cs.id) as sessions_created
        FROM users u
        LEFT JOIN case_sessions cs ON u.id = cs.created_by
        WHERE u.is_active = 1
        GROUP BY u.id, u.full_name
        ORDER BY sessions_created DESC
    """)
    
    # Notes created by user
    notes_by_user = db_manager.execute_query("""
        SELECT u.full_name, COUNT(cn.id) as notes_created
        FROM users u
        LEFT JOIN case_notes cn ON u.id = cn.created_by
        WHERE u.is_active = 1
        GROUP BY u.id, u.full_name
        ORDER BY notes_created DESC
    """)
    
    return {
        "cases_by_user": cases_by_user,
        "sessions_by_user": sessions_by_user,
        "notes_by_user": notes_by_user
    }

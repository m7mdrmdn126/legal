from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import json

from dependencies.auth import get_current_user
from models.user import User
from config.database import db_manager

router = APIRouter(prefix="/print", tags=["Print"])

class PrintManager:
    """Print-friendly document generator"""
    
    def __init__(self):
        self.base_style = """
        <style>
            @media print {
                body { font-size: 12px; font-family: Arial, sans-serif; }
                .no-print { display: none !important; }
                .page-break { page-break-before: always; }
                table { width: 100%; border-collapse: collapse; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
                th { background-color: #f5f5f5; font-weight: bold; }
                .header { text-align: center; margin-bottom: 20px; }
                .footer { position: fixed; bottom: 0; width: 100%; text-align: center; font-size: 10px; }
            }
            @media screen {
                body { font-family: Arial, sans-serif; margin: 20px; }
                .print-controls { margin-bottom: 20px; padding: 10px; background: #f0f0f0; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: right; }
                th { background-color: #4CAF50; color: white; }
                tr:nth-child(even) { background-color: #f2f2f2; }
                .header { text-align: center; margin-bottom: 30px; }
            }
            body { direction: rtl; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
            .stat-card { border: 1px solid #ddd; padding: 15px; text-align: center; }
            .stat-number { font-size: 24px; font-weight: bold; color: #2196F3; }
            .chart-placeholder { border: 1px dashed #ccc; padding: 20px; text-align: center; margin: 20px 0; }
        </style>
        """
    
    def generate_case_report(self, case_id: int) -> str:
        """Generate printable case report"""
        
        # Get case details
        case = db_manager.execute_query("""
            SELECT c.id, c.case_number, c.plaintiff, c.defendant,
                   ct.name as case_type, c.judgment_type,
                   c.created_at, c.updated_at
            FROM cases c
            JOIN case_types ct ON c.case_type_id = ct.id
            WHERE c.id = ?
        """, (case_id,))
        
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        case = case[0]
        
        # Get sessions
        sessions = db_manager.execute_query("""
            SELECT * FROM case_sessions 
            WHERE case_id = ? 
            ORDER BY session_date DESC
        """, (case_id,))
        
        # Get notes
        notes = db_manager.execute_query("""
            SELECT cn.*, u.full_name as created_by_name
            FROM case_notes cn
            LEFT JOIN users u ON cn.created_by = u.id
            WHERE cn.case_id = ?
            ORDER BY cn.created_at DESC
        """, (case_id,))
        
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>تقرير القضية - {case['case_number']}</title>
            {self.base_style}
        </head>
        <body>
            <div class="print-controls no-print">
                <button onclick="window.print()">طباعة</button>
                <button onclick="window.close()">إغلاق</button>
            </div>
            
            <div class="header">
                <h1>تقرير القضية</h1>
                <h2>رقم القضية: {case['case_number']}</h2>
                <p>تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')} (ميلادي)</p>
            </div>
            
            <div class="case-details">
                <h3>تفاصيل القضية</h3>
                <table>
                    <tr><th>رقم القضية</th><td>{case['case_number']}</td></tr>
                    <tr><th>المدعي</th><td>{case['plaintiff']}</td></tr>
                    <tr><th>المدعى عليه</th><td>{case['defendant']}</td></tr>
                    <tr><th>موضوع القضية</th><td>{case.get('case_subject', '')}</td></tr>
                    <tr><th>نوع القضية</th><td>{case['case_type_name']}</td></tr>
                    <tr><th>نوع الحكم</th><td>{case.get('judgment_type', '')}</td></tr>
                    <tr><th>نوع الحكم</th><td>{case.get('judgment_type', '')}</td></tr>
                    <tr><th>المحكمة</th><td>{case.get('court_name', '')}</td></tr>
                    <tr><th>تاريخ الإنشاء</th><td>{case['created_at']}</td></tr>
                    <tr><th>منشئ بواسطة</th><td>{case.get('created_by_name', '')}</td></tr>
                </table>
            </div>
        """
        
        # Add sessions section
        if sessions:
            html += f"""
            <div class="page-break"></div>
            <div class="sessions-section">
                <h3>جلسات القضية ({len(sessions)} جلسة)</h3>
                <table>
                    <thead>
                        <tr>
                            <th>تاريخ الجلسة</th>
                            <th>وقت الجلسة</th>
                            <th>المحكمة</th>
                            <th>نوع الجلسة</th>
                            <th>نوع الحكم</th>
                            <th>الملاحظات</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for session in sessions:
                html += f"""
                        <tr>
                            <td>{session.get('session_date', '')}</td>
                            <td>{session.get('session_time', '')}</td>
                            <td>{session.get('court_name', '')}</td>
                            <td>{session.get('session_type', '')}</td>
                            <td>{session.get('session_status', '')}</td>
                            <td>{session.get('session_notes', '')}</td>
                        </tr>
                """
            
            html += """
                    </tbody>
                </table>
            </div>
            """
        
        # Add notes section
        if notes:
            html += f"""
            <div class="page-break"></div>
            <div class="notes-section">
                <h3>ملاحظات القضية ({len(notes)} ملاحظة)</h3>
                <table>
                    <thead>
                        <tr>
                            <th>العنوان</th>
                            <th>الفئة</th>
                            <th>النوع</th>
                            <th>المحتوى</th>
                            <th>تاريخ الإنشاء</th>
                            <th>منشئ بواسطة</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for note in notes:
                content = note.get('content', '')[:100] + '...' if len(note.get('content', '')) > 100 else note.get('content', '')
                html += f"""
                        <tr>
                            <td>{note.get('title', '')}</td>
                            <td>{note.get('category', '')}</td>
                            <td>{note.get('note_type', '')}</td>
                            <td>{content}</td>
                            <td>{note.get('created_at', '')}</td>
                            <td>{note.get('created_by_name', '')}</td>
                        </tr>
                """
            
            html += """
                    </tbody>
                </table>
            </div>
            """
        
        html += """
            <div class="footer no-print">
                <p>نظام إدارة القضايا القانونية - تم إنتاج هذا التقرير في {}</p>
            </div>
        </body>
        </html>
        """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' (ميلادي)')
        
        return html
    
    def generate_cases_list_report(self, date_from: Optional[date] = None, 
                                 date_to: Optional[date] = None, 
                                 status: Optional[str] = None) -> str:
        """Generate printable cases list report"""
        
        # Build query
        base_query = """
            SELECT c.id, c.case_number, c.plaintiff, c.defendant,
                   ct.name as case_type, c.judgment_type,
                   c.created_at, c.updated_at
            FROM cases c
            JOIN case_types ct ON c.case_type_id = ct.id
            WHERE 1=1
        """
        
        params = []
        filters = []
        
        if date_from:
            base_query += " AND date(c.created_at) >= ?"
            params.append(date_from.isoformat())
            filters.append(f"من تاريخ: {date_from}")
        
        if date_to:
            base_query += " AND date(c.created_at) <= ?"
            params.append(date_to.isoformat())
            filters.append(f"إلى تاريخ: {date_to}")
        
        if status:
            base_query += " AND c.judgment_type = ?"
            params.append(status)
            filters.append(f"نوع الحكم: {status}")
        
        base_query += " ORDER BY c.created_at DESC"
        
        cases = db_manager.execute_query(base_query, tuple(params))
        
        # Generate statistics
        total_cases = len(cases)
        
        filter_info = " | ".join(filters) if filters else "جميع القضايا"
        
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>تقرير قائمة القضايا</title>
            {self.base_style}
        </head>
        <body>
            <div class="print-controls no-print">
                <button onclick="window.print()">طباعة</button>
                <button onclick="window.close()">إغلاق</button>
            </div>
            
            <div class="header">
                <h1>تقرير قائمة القضايا</h1>
                <p>المرشحات: {filter_info}</p>
                <p>إجمالي القضايا: {total_cases}</p>
                <p>تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')} (ميلادي)</p>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>رقم القضية</th>
                        <th>المدعي</th>
                        <th>المدعى عليه</th>
                        <th>نوع القضية</th>
                        <th>نوع الحكم</th>
                        <th>نوع الحكم</th>
                        <th>المحكمة</th>
                        <th>تاريخ الإنشاء</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for case in cases:
            html += f"""
                    <tr>
                        <td>{case['case_number']}</td>
                        <td>{case['plaintiff']}</td>
                        <td>{case['defendant']}</td>
                        <td>{case['case_type']}</td>
                        <td>{case.get('judgment_type', '')}</td>
                        <td>{case.get('judgment_type', '')}</td>
                        <td>{case.get('court_name', '')}</td>
                        <td>{case['created_at']}</td>
                    </tr>
            """
        
        html += f"""
                </tbody>
            </table>
            
            <div class="footer">
                <p>نظام إدارة القضايا القانونية - تم إنتاج هذا التقرير في {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def generate_dashboard_report(self) -> str:
        """Generate printable dashboard report"""
        
        # Get dashboard statistics
        stats = db_manager.execute_query("SELECT COUNT(*) as count FROM cases")[0]['count']
        total_users = db_manager.execute_query("SELECT COUNT(*) as count FROM users WHERE is_active = 1")[0]['count']
        total_sessions = db_manager.execute_query("SELECT COUNT(*) as count FROM case_sessions")[0]['count']
        total_notes = db_manager.execute_query("SELECT COUNT(*) as count FROM case_notes")[0]['count']
        
        # Cases by judgment type
        cases_by_judgment = db_manager.execute_query("""
            SELECT judgment_type, COUNT(*) as count 
            FROM cases 
            GROUP BY judgment_type 
            ORDER BY count DESC
        """)
        
        # Cases by type
        cases_by_type = db_manager.execute_query("""
            SELECT ct.name, COUNT(c.id) as count 
            FROM case_types ct 
            LEFT JOIN cases c ON ct.id = c.case_type_id 
            GROUP BY ct.name 
            ORDER BY count DESC 
            LIMIT 10
        """)
        
        # Recent cases
        recent_cases = db_manager.execute_query("""
            SELECT c.case_number, c.plaintiff, c.defendant, c.created_at
            FROM cases c
            ORDER BY c.created_at DESC
            LIMIT 10
        """)
        
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>تقرير لوحة التحكم</title>
            {self.base_style}
        </head>
        <body>
            <div class="print-controls no-print">
                <button onclick="window.print()">طباعة</button>
                <button onclick="window.close()">إغلاق</button>
            </div>
            
            <div class="header">
                <h1>تقرير لوحة التحكم</h1>
                <p>تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')} (ميلادي)</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats}</div>
                    <div>إجمالي القضايا</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_users}</div>
                    <div>إجمالي المستخدمين</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_sessions}</div>
                    <div>إجمالي الجلسات</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_notes}</div>
                    <div>إجمالي الملاحظات</div>
                </div>
            </div>
            
            <h3>القضايا حسب نوع الحكم</h3>
            <table>
                <thead>
                    <tr><th>نوع الحكم</th><th>عدد القضايا</th></tr>
                </thead>
                <tbody>
        """
        
        for status in cases_by_judgment:
            html += f"<tr><td>{status.get('judgment_type', 'غير محدد')}</td><td>{status['count']}</td></tr>"
        
        html += """
                </tbody>
            </table>
            
            <h3>القضايا حسب النوع</h3>
            <table>
                <thead>
                    <tr><th>نوع القضية</th><th>عدد القضايا</th></tr>
                </thead>
                <tbody>
        """
        
        for case_type in cases_by_type:
            html += f"<tr><td>{case_type['name']}</td><td>{case_type['count']}</td></tr>"
        
        html += """
                </tbody>
            </table>
            
            <h3>أحدث القضايا</h3>
            <table>
                <thead>
                    <tr><th>رقم القضية</th><th>المدعي</th><th>المدعى عليه</th><th>تاريخ الإنشاء</th></tr>
                </thead>
                <tbody>
        """
        
        for case in recent_cases:
            html += f"""<tr>
                <td>{case['case_number']}</td>
                <td>{case['plaintiff']}</td>
                <td>{case['defendant']}</td>
                <td>{case['created_at']}</td>
            </tr>"""
        
        html += f"""
                </tbody>
            </table>
            
            <div class="footer">
                <p>نظام إدارة القضايا القانونية - تم إنتاج هذا التقرير في {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (ميلادي)</p>
            </div>
        </body>
        </html>
        """
        
        return html

# Initialize print manager
print_manager = PrintManager()

@router.get("/case/{case_id}", response_class=HTMLResponse)
async def print_case_report(
    case_id: int,
    current_user: User = Depends(get_current_user)
):
    """Generate printable case report"""
    html = print_manager.generate_case_report(case_id)
    return HTMLResponse(content=html, status_code=200)

@router.get("/cases", response_class=HTMLResponse)
async def print_cases_list(
    date_from: Optional[date] = Query(None, description="Start date filter"),
    date_to: Optional[date] = Query(None, description="End date filter"),
    status: Optional[str] = Query(None, description="Case status filter"),
    current_user: User = Depends(get_current_user)
):
    """Generate printable cases list report"""
    html = print_manager.generate_cases_list_report(date_from, date_to, status)
    return HTMLResponse(content=html, status_code=200)

@router.get("/dashboard", response_class=HTMLResponse)
async def print_dashboard_report(
    current_user: User = Depends(get_current_user)
):
    """Generate printable dashboard report"""
    html = print_manager.generate_dashboard_report()
    return HTMLResponse(content=html, status_code=200)

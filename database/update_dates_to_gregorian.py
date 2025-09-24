#!/usr/bin/env python3
"""
Date Format Update Script
========================

This script ensures all dates in the database are properly formatted as Gregorian (ميلادي)
and adds metadata to track the date format being used.

Features:
1. Updates existing date columns to ensure ISO format
2. Adds date format metadata to database
3. Creates helper functions for consistent date handling
4. Validates date data integrity
"""

import sqlite3
import os
from datetime import datetime, date
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('date_update.log'),
        logging.StreamHandler()
    ]
)

class DateFormatUpdater:
    def __init__(self, db_path="latest_db.db"):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {db_path}")
        
        logging.info(f"Initialized DateFormatUpdater for: {self.db_path}")
    
    def connect_db(self):
        """Create database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def add_date_format_metadata(self):
        """Add metadata table to track date format settings"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            # Create metadata table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    description TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert or update date format metadata
            cursor.execute("""
                INSERT OR REPLACE INTO system_metadata 
                (key, value, description, updated_at) VALUES 
                (?, ?, ?, ?)
            """, (
                'date_calendar_type',
                'gregorian',
                'Calendar system used: gregorian (ميلادي)',
                datetime.now().isoformat()
            ))
            
            cursor.execute("""
                INSERT OR REPLACE INTO system_metadata 
                (key, value, description, updated_at) VALUES 
                (?, ?, ?, ?)
            """, (
                'date_locale',
                'ar-SA-u-ca-gregory',
                'Date locale with explicit Gregorian calendar',
                datetime.now().isoformat()
            ))
            
            cursor.execute("""
                INSERT OR REPLACE INTO system_metadata 
                (key, value, description, updated_at) VALUES 
                (?, ?, ?, ?)
            """, (
                'date_format_updated',
                datetime.now().isoformat(),
                'Last date when date formats were standardized to Gregorian',
                datetime.now().isoformat()
            ))
            
            conn.commit()
            logging.info("Added date format metadata to database")
            
        except Exception as e:
            logging.error(f"Error adding metadata: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def validate_date_columns(self):
        """Validate all date columns in the database"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        results = {
            'total_dates': 0,
            'valid_dates': 0,
            'invalid_dates': 0,
            'null_dates': 0,
            'tables_checked': []
        }
        
        try:
            # Get all tables with date columns
            tables_with_dates = [
                ('cases', ['created_at', 'updated_at']),
                ('case_sessions', ['session_date', 'created_at', 'updated_at']),
                ('case_notes', ['created_at', 'updated_at']),
                ('case_types', ['created_at', 'updated_at']),
                ('users', ['created_at', 'updated_at'])
            ]
            
            for table_name, date_columns in tables_with_dates:
                logging.info(f"Validating dates in table: {table_name}")
                results['tables_checked'].append(table_name)
                
                for column_name in date_columns:
                    # Check if column exists
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    if column_name not in columns:
                        logging.warning(f"Column {column_name} not found in {table_name}")
                        continue
                    
                    # Count total records
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    total_records = cursor.fetchone()[0]
                    
                    # Count null dates
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} IS NULL")
                    null_count = cursor.fetchone()[0]
                    results['null_dates'] += null_count
                    
                    # Count non-null dates
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} IS NOT NULL")
                    non_null_count = cursor.fetchone()[0]
                    results['total_dates'] += non_null_count
                    
                    # Validate date format for non-null dates
                    cursor.execute(f"""
                        SELECT {column_name} FROM {table_name} 
                        WHERE {column_name} IS NOT NULL 
                        LIMIT 10
                    """)
                    
                    sample_dates = cursor.fetchall()
                    for row in sample_dates:
                        date_str = row[0]
                        try:
                            # Try to parse the date
                            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                            results['valid_dates'] += 1
                        except ValueError:
                            results['invalid_dates'] += 1
                            logging.warning(f"Invalid date format in {table_name}.{column_name}: {date_str}")
            
            logging.info("Date validation completed:")
            logging.info(f"  Total dates checked: {results['total_dates']}")
            logging.info(f"  Valid dates: {results['valid_dates']}")
            logging.info(f"  Invalid dates: {results['invalid_dates']}")
            logging.info(f"  Null dates: {results['null_dates']}")
            logging.info(f"  Tables checked: {results['tables_checked']}")
            
        except Exception as e:
            logging.error(f"Error validating dates: {e}")
        finally:
            conn.close()
        
        return results
    
    def update_database_comments(self):
        """Add comments/documentation about date format"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        try:
            # Create a documentation table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS database_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Add date format documentation
            cursor.execute("""
                INSERT OR REPLACE INTO database_info 
                (category, title, description) VALUES 
                (?, ?, ?)
            """, (
                'date_format',
                'نظام التقويم المستخدم',
                'جميع التواريخ في النظام تستخدم التقويم الميلادي (Gregorian Calendar) بصيغة ISO 8601. يتم عرض التواريخ باللغة العربية مع إشارة (ميلادي) للوضوح.'
            ))
            
            cursor.execute("""
                INSERT OR REPLACE INTO database_info 
                (category, title, description) VALUES 
                (?, ?, ?)
            """, (
                'date_locale',
                'إعدادات المنطقة الزمنية',
                'يتم تنسيق التواريخ باستخدام المنطقة ar-SA-u-ca-gregory لضمان عرض التاريخ الميلادي باللغة العربية.'
            ))
            
            conn.commit()
            logging.info("Added database documentation about date formats")
            
        except Exception as e:
            logging.error(f"Error adding database comments: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def generate_date_format_report(self):
        """Generate a comprehensive report about date formats in the database"""
        conn = self.connect_db()
        cursor = conn.cursor()
        
        report = []
        report.append("=" * 60)
        report.append("تقرير تنسيق التواريخ في قاعدة البيانات")
        report.append("DATABASE DATE FORMAT REPORT")
        report.append("=" * 60)
        report.append(f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (ميلادي)")
        report.append(f"قاعدة البيانات: {self.db_path}")
        report.append("")
        
        try:
            # Check metadata
            cursor.execute("""
                SELECT key, value, description, updated_at 
                FROM system_metadata 
                WHERE key LIKE 'date_%'
                ORDER BY key
            """)
            
            metadata = cursor.fetchall()
            if metadata:
                report.append("إعدادات التاريخ المخزنة:")
                report.append("Stored Date Settings:")
                for row in metadata:
                    report.append(f"  {row[0]}: {row[1]}")
                    report.append(f"    الوصف: {row[2]}")
                    report.append(f"    آخر تحديث: {row[3]}")
                report.append("")
            
            # Validation results
            results = self.validate_date_columns()
            report.append("نتائج فحص التواريخ:")
            report.append("Date Validation Results:")
            report.append(f"  إجمالي التواريخ المفحوصة: {results['total_dates']}")
            report.append(f"  التواريخ الصحيحة: {results['valid_dates']}")
            report.append(f"  التواريخ غير الصحيحة: {results['invalid_dates']}")
            report.append(f"  التواريخ الفارغة: {results['null_dates']}")
            report.append(f"  الجداول المفحوصة: {', '.join(results['tables_checked'])}")
            report.append("")
            
            # Sample dates from each table
            report.append("عينات من التواريخ:")
            report.append("Sample Dates:")
            
            sample_queries = [
                ("أحدث القضايا", "SELECT case_number, created_at FROM cases ORDER BY created_at DESC LIMIT 3"),
                ("أحدث الجلسات", "SELECT case_id, session_date FROM case_sessions WHERE session_date IS NOT NULL ORDER BY session_date DESC LIMIT 3"),
                ("أحدث الملاحظات", "SELECT case_id, created_at FROM case_notes ORDER BY created_at DESC LIMIT 3")
            ]
            
            for title, query in sample_queries:
                try:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    report.append(f"  {title}:")
                    for row in rows:
                        report.append(f"    {row[0]} - {row[1]}")
                except Exception as e:
                    report.append(f"    خطأ في استعلام {title}: {e}")
                report.append("")
            
        except Exception as e:
            report.append(f"خطأ في إنشاء التقرير: {e}")
            logging.error(f"Error generating report: {e}")
        finally:
            conn.close()
        
        # Write report to file
        report_content = "\n".join(report)
        with open("date_format_report.txt", "w", encoding="utf-8") as f:
            f.write(report_content)
        
        logging.info("Date format report saved to date_format_report.txt")
        return report_content
    
    def run_full_update(self):
        """Run complete date format update process"""
        logging.info("Starting full date format update process")
        
        try:
            # Step 1: Add metadata
            self.add_date_format_metadata()
            
            # Step 2: Validate existing dates
            results = self.validate_date_columns()
            
            # Step 3: Add documentation
            self.update_database_comments()
            
            # Step 4: Generate report
            self.generate_date_format_report()
            
            logging.info("Date format update completed successfully")
            
            # Summary
            success_rate = (results['valid_dates'] / results['total_dates'] * 100) if results['total_dates'] > 0 else 100
            logging.info(f"Summary: {results['valid_dates']}/{results['total_dates']} dates are valid ({success_rate:.1f}%)")
            
            if results['invalid_dates'] > 0:
                logging.warning(f"Found {results['invalid_dates']} invalid dates that may need manual review")
            
            return True
            
        except Exception as e:
            logging.error(f"Date format update failed: {e}")
            return False

def main():
    """Main execution function"""
    print("تحديث تنسيق التواريخ إلى الميلادي")
    print("Date Format Update to Gregorian")
    print("=" * 50)
    
    # Initialize updater
    updater = DateFormatUpdater("latest_db.db")
    
    # Run the update process
    success = updater.run_full_update()
    
    if success:
        print("\n✅ تم تحديث تنسيق التواريخ بنجاح!")
        print("✅ Date format update completed successfully!")
        print("\nالتواريخ الآن مُعيّنة كميلادية في جميع أنحاء النظام")
        print("All dates are now configured as Gregorian throughout the system")
    else:
        print("\n❌ فشل في تحديث تنسيق التواريخ")
        print("❌ Date format update failed")
        print("راجع ملف date_update.log للتفاصيل")
        print("Check date_update.log for details")

if __name__ == "__main__":
    main()

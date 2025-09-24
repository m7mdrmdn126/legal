#!/usr/bin/env python3
"""
Legal Cases Database Migration Script
====================================
Migrates data from old database (oldData.db) to new standardized database (latest_db.db)

Author: AI Assistant
Date: September 24, 2025
"""

import sqlite3
import json
import re
from datetime import datetime
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    def __init__(self, old_db_path, new_db_path):
        self.old_db_path = old_db_path
        self.new_db_path = new_db_path
        self.migration_stats = {
            'total_old_cases': 0,
            'migrated_cases': 0,
            'created_sessions': 0,
            'created_notes': 0,
            'skipped_cases': 0,
            'errors': []
        }
        
        # Case type standardization mapping
        self.case_type_mapping = {
            # محو بيانات variants
            'محو بيانات': 'محو بيانات',
            'محو البيانات': 'محو بيانات',
            'محو  بيانات': 'محو بيانات',
            ' محو بيانات': 'محو بيانات',
            'فهرس الدعاوي محو بيانات': 'محو بيانات',
            'محو و شطب': 'محو بيانات',
            'محو وشطب': 'محو بيانات',
            'محو وشطب ': 'محو بيانات',
            'محوبيانات': 'محو بيانات',
            'محو بيانتت': 'محو بيانات',
            'محو بيانت ': 'محو بيانات',
            'محو بياناتذ': 'محو بيانات',
            'محو بياانات': 'محو بيانات',
            'محمو بيانات': 'محو بيانات',
            
            # تعويضات variants
            'فهرس دعاوى التعويض': 'تعويضات',
            'تعويضات': 'تعويضات',
            'تعويض مدني': 'تعويضات',
            'تعويض إداري': 'تعويضات',
            'تعويض مدنى إسكندرية': 'تعويضات',
            'تعويض إداري القاهرة': 'تعويضات',
            'تعويض ': 'تعويضات',
            
            # تصاريح إدارية variants
            'تصاريح': 'تصاريح إدارية',
            'تصاريح مالية و إدارية - أفراد': 'تصاريح إدارية',
            'تصاريح مالية و إدارية - ضباط': 'تصاريح إدارية',
            'تصاريح مالية و إدارية - مدنيين': 'تصاريح إدارية',
            'تصريه مالية و ادارية - ظباط': 'تصاريح إدارية',
            'تصريح مالية و ادارية - افراد': 'تصاريح إدارية',
            'تصريح ماليه و الاداريه -  افراد': 'تصاريح إدارية',
            'تصريح ماليه و اداريه - افراد': 'تصاريح إدارية',
            'تصريح مالية وإدارية - أفراد': 'تصاريح إدارية',
            'تصريح مالية و ادراية - افراد': 'تصاريح إدارية',
            'تصريح مالية و ادرارية - افراد': 'تصاريح إدارية',
            'تصريح مالية و اداريه - افراد': 'تصاريح إدارية',
            'تصريح مالية و ادارية - افراد ': 'تصاريح إدارية',
            'تصاريح مالية و إدارية - أفراد ': 'تصاريح إدارية',
            'تصاريح مالية و إدارية - أظباط ': 'تصاريح إدارية',
            'طلب مالية و ادارية - افراد': 'تصاريح إدارية',
            'طلب مالية و ادارية - افراد ': 'تصاريح إدارية',
            
            # أمور مالية variants
            'نفقات افراد': 'أمور مالية',
            'نفقات أفراد': 'أمور مالية',
            'نفقات ضباط': 'أمور مالية',
            'نفقات مدنيين': 'أمور مالية',
            'رصيد اجازات افراد': 'أمور مالية',
            'رصيد اجازات مدنيين': 'أمور مالية',
            'رصيد الإجازات': 'أمور مالية',
            'رصيد إجازات أفراد': 'أمور مالية',
            'رصيد إجازات مدنيين': 'أمور مالية',
            'مرتبات العاملين': 'أمور مالية',
            'مرتبات العاملين المدنيين': 'أمور مالية',
            'حافز التطوير 150%': 'أمور مالية',
            'معاشات': 'أمور مالية',
            'معاش الأجر الأساسي -مرور': 'أمور مالية',
            'كــــشـــف نــفــقـــات الأفراد': 'أمور مالية',
            
            # تلفيات السيارات variants
            'تلفيات سيارات': 'تلفيات السيارات',
            'تلفيات سيارات ': 'تلفيات السيارات',
            'تبفيات سيارات': 'تلفيات السيارات',
            'تبفيات سيارات ': 'تلفيات السيارات',
            'تليفات سيارات ': 'تلفيات السيارات',
            'تلفيات سيارت': 'تلفيات السيارات',
            'تلفيات سيارات ضمتداولة ': 'تلفيات السيارات',
            ' تلفيات سيارات ': 'تلفيات السيارات',
            'مصادمة ومتوفى': 'تلفيات السيارات',
            
            # شؤون المرور variants
            'موظفي المرور- حوافز وبدالات': 'شؤون المرور',
            'موظفي المرور - حوافز وبدالات': 'شؤون المرور',
            'موظفين مرور رصيد اجازات': 'شؤون المرور',
            'موظفي المرور - رصيد إجازات': 'شؤون المرور',
            'موظفي المرور - ترقيات': 'شؤون المرور',
            'موظفي المرور - ترقيات ': 'شؤون المرور',
            'موظفين مرور ترقيات': 'شؤون المرور',
            'موظفي  المرور رصيد اجازات': 'شؤون المرور',
            'موظفي  المرور رصيد اجازات ': 'شؤون المرور',
            'موظفين مرو بدالات': 'شؤون المرور',
            'شكاوى المرور': 'شؤون المرور',
            
            # تصاريح أمنية variants
            'تصاريح - البحث الجنائي': 'تصاريح أمنية',
            'تصاريح البحث الجنائي': 'تصاريح أمنية',
            'تصاريح- البحث الجنائي': 'تصاريح أمنية',
            'تصاريح-البحث الجنائي': 'تصاريح أمنية',
            'تصاريح -البحث الجنائي': 'تصاريح أمنية',
            '.تصاريح - البحث الجنائي': 'تصاريح أمنية',
            'تصريح بحث جنائي': 'تصاريح أمنية',
            'تصريح اداره بحث جنائي': 'تصاريح أمنية',
            'تصريح اداره البحث الجنائي': 'تصاريح أمنية',
            'تصريح - بحث جنائي': 'تصاريح أمنية',
            'تصريح - البحث الجنائي': 'تصاريح أمنية',
            'تصاريح – المعلومات الجنائية': 'تصاريح أمنية',
            'تصاريح المعلومات الجنائية': 'تصاريح أمنية',
            'تصاريح- المعلومات الجنائية': 'تصاريح أمنية',
            'تصاريح-المعلومات الجنائية': 'تصاريح أمنية',
            'تصاريح - المعلومات الجنائية': 'تصاريح أمنية',
            'تصاريح – إدارة النجدة': 'تصاريح أمنية',
            'تصاريح إدارة النجدة': 'تصاريح أمنية',
            'تصاريح- إدارة النجدة': 'تصاريح أمنية',
            'تصاريح-إدارة النجدة': 'تصاريح أمنية',
            'تصاريح _ إدارة النجدة': 'تصاريح أمنية',
            'تصاريح-إدارة النجدة ': 'تصاريح أمنية',
            'تصاريح تنفيذ الأحكام': 'تصاريح أمنية',
            'تصاريح-تنفيذ الأحكام': 'تصاريح أمنية',
            'تصاريح- تنفيذ الأحكام': 'تصاريح أمنية',
            'تصاريح-تفيذ الأحكام ': 'تصاريح أمنية',
            'تصاريح -تنفيذ الأحكام ': 'تصاريح أمنية',
            'تصاريح - تنفيذ الأحكام ': 'تصاريح أمنية',
            'تصاريح - تنفيذ الحكام ': 'تصاريح أمنية',
            'تصريح تنفيذ احكام ': 'تصاريح أمنية',
            'تصاريح عامة': 'تصاريح أمنية',
            'تصارح-قسم الرخص': 'تصاريح أمنية',
            'جدول تصاريح المعلومات الجنائية': 'تصاريح أمنية',
            
            # قضايا الأسلحة variants
            'فهرس دعاوي السلاح': 'قضايا الأسلحة',
            'دعاوي السلاح': 'قضايا الأسلحة',
            ' دعاوي السلاح': 'قضايا الأسلحة',
            'قضايا الأسلحة': 'قضايا الأسلحة',
            'رخص الأسلحة': 'قضايا الأسلحة',
            'إلغاء رخصة محل أسلحة وزخائر': 'قضايا الأسلحة',
            'سلاح': 'قضايا الأسلحة',
            'دعوى بطلان رخصة سلاح': 'قضايا الأسلحة',
            
            # جنح مباشرة variants
            'جنحة مباشرة': 'جنح مباشرة',
            'جنحة مباشرة ': 'جنح مباشرة',
            'جنحة مباشره': 'جنح مباشرة',
            'جنحه ماشرة': 'جنح مباشرة',
            'جنحه مباشرة': 'جنح مباشرة',
            'جنحه مباشرة ': 'جنح مباشرة',
            'جنح مباشره': 'جنح مباشرة',
            'جنحه ماشرة ': 'جنح مباشرة',
            'جنحة مباشرة -الامتناع عن تنفيذ الحكم رقم /4773لسنة 74 ق': 'جنح مباشرة',
            'جنحة مباشرة - زعم الامتناع عن تنفيذ حكم': 'جنح مباشرة',
            'جنحة مباشرة - الامتناع عن تنفيذ الحكم رقم /24752 لسنة72ق': 'جنح مباشرة',
            
            # قضايا شخصية variants
            'قضايا ضباط': 'قضايا شخصية',
            'قضايا ضباط ': 'قضايا شخصية',
            'قضايا أفراد': 'قضايا شخصية',
            'هدايا ضباط': 'قضايا شخصية',
            
            # أتعاب المحاماة variants
            'أتعاب المحاماة': 'أتعاب المحاماة',
            'اتعاب المحاماه': 'أتعاب المحاماة',
            'اتعاب المحاماه ': 'أتعاب المحاماة',
            'اتعاب محاماه ': 'أتعاب المحاماة',
            
            # إجراءات قضائية variants
            'طلب سحب صيغ تنفيذية': 'إجراءات قضائية',
            'إنذارات': 'إجراءات قضائية',
            'مطالبة': 'إجراءات قضائية',
            
            # مقار ومرافق variants
            'مقار شرطيه': 'مقار ومرافق',
            'مقرات شرطية': 'مقار ومرافق',
            'مقار شرطية': 'مقار ومرافق',
            'مقرات شرطيه': 'مقار ومرافق',
            
            # فحص وتحريات variants
            'فحص': 'فحص وتحريات',
            'فحص ': 'فحص وتحريات',
            'تحريات': 'فحص وتحريات',
        }
        
        # Standard case types to insert
        self.standard_case_types = [
            'محو بيانات',
            'تعويضات', 
            'تصاريح إدارية',
            'أمور مالية',
            'تلفيات السيارات',
            'شؤون المرور',
            'تصاريح أمنية',
            'قضايا الأسلحة',
            'جنح مباشرة',
            'قضايا شخصية',
            'أتعاب المحاماة',
            'إجراءات قضائية',
            'مقار ومرافق',
            'فحص وتحريات',
            'متنوع'
        ]

    def clean_field(self, value):
        """Clean field value by removing placeholders"""
        if not value or value in ['---', '.', '-', '', 'NULL']:
            return None
        return str(value).strip()

    def is_valid_case_number(self, case_number):
        """Check if case number is valid (not a name)"""
        if not case_number:
            return False
        
        # Check for Arabic name patterns (contains multiple Arabic words)
        arabic_words = re.findall(r'[\u0600-\u06FF]+', case_number)
        if len(arabic_words) >= 3:  # Likely a name if 3+ Arabic words
            return False
            
        # Check for obvious invalid patterns
        invalid_patterns = ['.', '--', 'محمد', 'أحمد', 'عبد', 'إبراهيم', 'علي']
        for pattern in invalid_patterns:
            if pattern in case_number:
                return False
                
        return True

    def generate_case_number(self, case_id):
        """Generate new case number for invalid entries"""
        return f"MIGRATED-{case_id}"

    def normalize_date(self, date_str):
        """Convert Arabic date format to ISO format"""
        if not date_str or date_str in ['---', '', None]:
            return None
            
        try:
            # Handle format like "26/6/2024"
            if '/' in date_str:
                parts = date_str.split('/')
                if len(parts) == 3:
                    day, month, year = parts
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}T00:00:00"
        except:
            pass
            
        return None

    def get_or_create_case_type_id(self, case_type_name, cursor):
        """Get case type ID, creating if necessary"""
        if not case_type_name:
            case_type_name = 'متنوع'
            
        # Map to standard type
        standard_type = self.case_type_mapping.get(case_type_name, 'متنوع')
        
        # Check if exists
        cursor.execute("SELECT id FROM case_types WHERE name = ?", (standard_type,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            # Create new case type
            cursor.execute(
                "INSERT INTO case_types (name, created_at, updated_at) VALUES (?, ?, ?)",
                (standard_type, datetime.now().isoformat(), datetime.now().isoformat())
            )
            return cursor.lastrowid

    def clean_new_database(self):
        """Clean test data from new database and insert standard case types"""
        logger.info("Cleaning new database and inserting standard case types...")
        
        conn = sqlite3.connect(self.new_db_path)
        cursor = conn.cursor()
        
        try:
            # Clear existing data
            cursor.execute("DELETE FROM case_notes")
            cursor.execute("DELETE FROM case_sessions") 
            cursor.execute("DELETE FROM cases")
            cursor.execute("DELETE FROM case_types")
            cursor.execute("DELETE FROM users WHERE user_type != 'admin'")
            
            # Insert standard case types
            for case_type in self.standard_case_types:
                cursor.execute(
                    "INSERT OR IGNORE INTO case_types (name, created_at, updated_at) VALUES (?, ?, ?)",
                    (case_type, datetime.now().isoformat(), datetime.now().isoformat())
                )
            
            conn.commit()
            logger.info(f"Inserted {len(self.standard_case_types)} standard case types")
            
        except Exception as e:
            logger.error(f"Error cleaning database: {e}")
            conn.rollback()
        finally:
            conn.close()

    def create_migration_notes(self, case_id, old_case, cursor):
        """Create notes from additional fields in old case"""
        notes = []
        
        # Map old fields to note entries
        field_mapping = {
            'الجهة_القضائية': 'الجهة القضائية',
            'رقم_الملف': 'رقم الملف',
            'رقم_الصادر_للمعلومات': 'رقم الصادر للمعلومات',
            'تاريخ_الصادر_للمعلومات': 'تاريخ الصادر للمعلومات', 
            'رقم_الصادر_للهيئة': 'رقم الصادر للهيئة',
            'تاريخ_الصادر_للهيئة': 'تاريخ الصادر للهيئة'
        }
        
        # Collect non-empty additional fields
        for old_field, display_name in field_mapping.items():
            try:
                value = self.clean_field(old_case[old_field])
                if value:
                    notes.append(f"{display_name}: {value}")
            except (KeyError, IndexError):
                continue
        
        # Add original notes if exists
        try:
            original_notes = self.clean_field(old_case['ملاحظات'])
            if original_notes:
                notes.append(f"الملاحظات الأصلية: {original_notes}")
        except (KeyError, IndexError):
            pass
            
        # Create combined note if we have data
        if notes:
            combined_notes = "معلومات إضافية من النظام القديم:\n" + "\n".join(notes)
            cursor.execute(
                "INSERT INTO case_notes (case_id, note_text, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (case_id, combined_notes, datetime.now().isoformat(), datetime.now().isoformat())
            )
            self.migration_stats['created_notes'] += 1

    def create_session_from_followup(self, case_id, old_case, cursor):
        """Create session from follow-up information"""
        try:
            followup = self.clean_field(old_case['المتابعة_القضائية'])
            if followup:
                cursor.execute(
                    "INSERT INTO case_sessions (case_id, session_notes, created_at, updated_at) VALUES (?, ?, ?, ?)",
                    (case_id, followup, datetime.now().isoformat(), datetime.now().isoformat())
                )
                self.migration_stats['created_sessions'] += 1
        except (KeyError, IndexError):
            pass

    def migrate_cases(self):
        """Main migration function"""
        logger.info("Starting case migration...")
        
        # Connect to databases
        old_conn = sqlite3.connect(self.old_db_path)
        old_conn.row_factory = sqlite3.Row  # Enable column access by name
        old_cursor = old_conn.cursor()
        
        new_conn = sqlite3.connect(self.new_db_path)
        new_cursor = new_conn.cursor()
        
        try:
            # Get all cases from old database
            old_cursor.execute("SELECT * FROM cases ORDER BY id")
            old_cases = old_cursor.fetchall()
            self.migration_stats['total_old_cases'] = len(old_cases)
            
            logger.info(f"Found {len(old_cases)} cases to migrate")
            
            # Track duplicate case numbers for session creation
            case_number_tracker = {}
            
            for old_case in old_cases:
                try:
                    # Clean and validate data
                    case_number = self.clean_field(old_case['رقم_الدعوى'])
                    plaintiff = self.clean_field(old_case['اسم_المدعي'])
                    defendant = self.clean_field(old_case['اسم_المدعي_عليه']) or 'غير محدد'
                    case_type_name = self.clean_field(old_case['نوع_القضية'])
                    
                    # Skip if no plaintiff
                    if not plaintiff:
                        logger.warning(f"Skipping case {old_case['id']}: No plaintiff")
                        self.migration_stats['skipped_cases'] += 1
                        continue
                    
                    # Validate/fix case number
                    if not self.is_valid_case_number(case_number):
                        case_number = self.generate_case_number(old_case['id'])
                        logger.info(f"Generated new case number: {case_number}")
                    
                    # Get case type ID
                    case_type_id = self.get_or_create_case_type_id(case_type_name, new_cursor)
                    
                    # Check for duplicate case numbers (for session creation)
                    case_key = f"{case_number}_{plaintiff}"
                    
                    if case_key in case_number_tracker:
                        # This is a duplicate - create as session of existing case
                        existing_case_id = case_number_tracker[case_key]
                        self.create_session_from_followup(existing_case_id, old_case, new_cursor)
                        self.create_migration_notes(existing_case_id, old_case, new_cursor)
                        logger.info(f"Created session for existing case {existing_case_id}")
                    else:
                        # Create new case
                        new_cursor.execute("""
                            INSERT INTO cases (
                                case_number, plaintiff, defendant, case_type_id, 
                                judgment_type, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            case_number, plaintiff, defendant, case_type_id,
                            'حكم اول',  # Default judgment type
                            datetime.now().isoformat(),
                            datetime.now().isoformat()
                        ))
                        
                        new_case_id = new_cursor.lastrowid
                        case_number_tracker[case_key] = new_case_id
                        
                        # Create notes from additional fields
                        self.create_migration_notes(new_case_id, old_case, new_cursor)
                        
                        # Create session from follow-up if exists
                        self.create_session_from_followup(new_case_id, old_case, new_cursor)
                        
                        self.migration_stats['migrated_cases'] += 1
                        
                        if self.migration_stats['migrated_cases'] % 100 == 0:
                            logger.info(f"Migrated {self.migration_stats['migrated_cases']} cases...")
                
                except Exception as e:
                    error_msg = f"Error migrating case {old_case['id']}: {e}"
                    logger.error(error_msg)
                    self.migration_stats['errors'].append(error_msg)
                    continue
            
            # Commit changes
            new_conn.commit()
            logger.info("Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Critical error during migration: {e}")
            new_conn.rollback()
            raise
        finally:
            old_conn.close()
            new_conn.close()

    def generate_report(self):
        """Generate migration report"""
        logger.info("Generating migration report...")
        
        report = f"""
LEGAL CASES DATABASE MIGRATION REPORT
====================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

MIGRATION STATISTICS:
====================
Total Old Cases: {self.migration_stats['total_old_cases']:,}
Successfully Migrated: {self.migration_stats['migrated_cases']:,}
Sessions Created: {self.migration_stats['created_sessions']:,}
Notes Generated: {self.migration_stats['created_notes']:,}
Skipped Cases: {self.migration_stats['skipped_cases']:,}
Errors: {len(self.migration_stats['errors'])}

SUCCESS RATE: {(self.migration_stats['migrated_cases']/self.migration_stats['total_old_cases']*100):.1f}%

CASE TYPE STANDARDIZATION:
========================
Original Types: ~53 variants
Standardized Types: {len(self.standard_case_types)}

ERRORS ENCOUNTERED:
==================
"""
        
        for error in self.migration_stats['errors'][:10]:  # Show first 10 errors
            report += f"- {error}\n"
        
        if len(self.migration_stats['errors']) > 10:
            report += f"... and {len(self.migration_stats['errors']) - 10} more errors\n"
        
        # Save report to file
        report_path = Path('migration_report.txt')
        report_path.write_text(report, encoding='utf-8')
        
        print(report)
        logger.info(f"Report saved to {report_path}")

    def run_migration(self):
        """Execute complete migration process"""
        logger.info("Starting complete migration process...")
        
        try:
            # Phase 1: Clean and prepare new database
            self.clean_new_database()
            
            # Phase 2: Migrate cases
            self.migrate_cases()
            
            # Phase 3: Generate report
            self.generate_report()
            
            logger.info("Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise


def main():
    """Main execution function"""
    # Database paths
    old_db_path = "old db /oldData.db"
    new_db_path = "latest_db.db"
    
    # Verify files exist
    if not Path(old_db_path).exists():
        print(f"Error: Old database not found at {old_db_path}")
        return
        
    if not Path(new_db_path).exists():
        print(f"Error: New database not found at {new_db_path}")
        return
    
    # Create migrator and run
    migrator = DatabaseMigrator(old_db_path, new_db_path)
    migrator.run_migration()


if __name__ == "__main__":
    main()

from config.database import db_manager
from utils.arabic import arabic_processor
from typing import List, Dict, Optional, Tuple

class DatabaseUtils:
    """Enhanced database utilities with Arabic search support"""
    
    def __init__(self):
        self.db = db_manager
    
    def paginate_query(self, base_query: str, params: tuple, page: int = 1, size: int = 40) -> Dict:
        """Execute paginated query with count"""
        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM ({base_query})"
        count_result = self.db.execute_query(count_query, params)
        total = count_result[0]['total'] if count_result else 0
        
        # Get paginated results
        offset = (page - 1) * size
        paginated_query = f"{base_query} LIMIT ? OFFSET ?"
        items = self.db.execute_query(paginated_query, params + (size, offset))
        
        # Calculate pagination info
        pages = (total + size - 1) // size  # Ceiling division
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }
    
    def build_search_conditions(self, search_term: str, fields: List[str]) -> Tuple[str, List[str]]:
        """Build SQL search conditions for Arabic text with comprehensive normalization"""
        if not search_term or not fields:
            return "", []
        
        # Get the original and normalized search terms
        original_term = search_term.strip()
        normalized_search = arabic_processor.prepare_search_term(search_term)
        
        # For Arabic text matching, we need a different approach
        # Since SQLite doesn't handle Arabic normalization well, we'll use REPLACE function
        # to normalize the database content on-the-fly for comparison
        
        conditions = []
        params = []
        
        for field in fields:
            field_conditions = []
            
            # Method 1: Direct match (case insensitive)
            field_conditions.append(f"LOWER({field}) LIKE LOWER(?)")
            params.append(f"%{original_term}%")
            
            # Method 2: Normalized comparison using nested REPLACE functions
            # This normalizes the database field content and compares with normalized search
            if normalized_search != original_term.lower():
                # Create a field expression that removes diacritics and normalizes characters
                normalized_field = field
                
                # Remove common diacritics from the field
                diacritics = ['ً', 'ٌ', 'ٍ', 'َ', 'ُ', 'ِ', 'ّ', 'ْ']
                for diacritic in diacritics:
                    normalized_field = f"REPLACE({normalized_field}, '{diacritic}', '')"
                
                # Normalize common character variations
                char_mappings = {
                    'أ': 'ا', 'إ': 'ا', 'آ': 'ا',  # Alef variations
                    'ة': 'ه',                        # Taa marbuta to haa
                    'ى': 'ي',                        # Alef maksura to yaa
                }
                
                for original_char, replacement_char in char_mappings.items():
                    normalized_field = f"REPLACE({normalized_field}, '{original_char}', '{replacement_char}')"
                
                # Compare normalized field with normalized search term
                field_conditions.append(f"LOWER({normalized_field}) LIKE LOWER(?)")
                params.append(f"%{normalized_search}%")
            
            # Method 3: More conservative flexible matching for diacritics  
            # Only apply flexible matching for short, clearly Arabic words
            diacritics = 'ًٌٍَُِّْ'
            if (not any(d in original_term for d in diacritics) and 
                any('\u0600' <= c <= '\u06FF' for c in original_term) and
                len(original_term.strip()) <= 6 and  # Only for short terms
                ' ' not in original_term.strip()):    # Only for single words
                
                word = original_term.strip()
                if len(word) >= 3:  # Only for meaningful words
                    # Create a more conservative flexible pattern
                    # Instead of %char%, use char followed by 0-2 characters
                    # This allows for diacritics but not unlimited gaps
                    
                    flexible_pattern = ""
                    for i, char in enumerate(word):
                        if i == 0:
                            flexible_pattern += char
                        else:
                            # Allow up to 2 characters (diacritics) between Arabic letters
                            flexible_pattern += f"__{char}"  # __ allows exactly 0-2 chars
                    
                    # Allow flexible matching for common Arabic words/names
                    # This helps with diacritics matching while avoiding overly broad matches
                    common_words = ['محمد', 'أحمد', 'إبراهيم', 'فاطمة', 'علي', 'الله', 'شركة', 'مؤسسة']
                    
                    if word in common_words or len(word) <= 4:  # Common words or short words
                        # Create a pattern that allows diacritics between letters
                        # For "محمد", this creates a pattern like "%م%ح%م%د%" to match "مُحَمَّد"
                        flexible_pattern = ""
                        for i, char in enumerate(word):
                            if i == 0:
                                flexible_pattern += f"%{char}"
                            else:
                                flexible_pattern += f"%{char}"
                        flexible_pattern += "%"
                        
                        field_conditions.append(f"LOWER({field}) LIKE LOWER(?)")
                        params.append(flexible_pattern)
            
            conditions.append(f"({' OR '.join(field_conditions)})")
        
        where_clause = " OR ".join(conditions)
        return f"({where_clause})", params

# Global database utilities instance
db_utils = DatabaseUtils()

import re

class ArabicTextProcessor:
    """Utility class for processing Arabic text for search"""
    
    # Arabic character mappings for normalization
    CHAR_MAPPINGS = {
        'أ': 'ا', 'إ': 'ا', 'آ': 'ا',  # Alef variations
        'ة': 'ه',                        # Taa marbuta to haa
        'ي': 'ى', 'ى': 'ي',             # Yaa variations
        'ؤ': 'و',                        # Waw with hamza
        'ئ': 'ي',                        # Yaa with hamza
    }
    
    # Diacritics (Tashkeel) to remove
    DIACRITICS = 'ًٌٍَُِّْ'
    
    @classmethod
    def normalize_text(cls, text: str) -> str:
        """
        Normalize Arabic text for better search matching
        - Remove diacritics
        - Normalize similar characters
        - Convert to lowercase
        """
        if not text:
            return ""
        
        # Remove diacritics
        normalized = ''.join(char for char in text if char not in cls.DIACRITICS)
        
        # Normalize characters
        for original, replacement in cls.CHAR_MAPPINGS.items():
            normalized = normalized.replace(original, replacement)
        
        # Convert to lowercase and strip whitespace
        return normalized.lower().strip()
    
    @classmethod
    def prepare_search_term(cls, search_term: str) -> str:
        """Prepare search term for database matching"""
        return cls.normalize_text(search_term)
    
    @classmethod
    def create_search_pattern(cls, search_term: str) -> str:
        """Create SQL LIKE pattern with normalized search term"""
        normalized = cls.prepare_search_term(search_term)
        return f"%{normalized}%"
    
    @classmethod
    def matches_search(cls, text: str, search_term: str) -> bool:
        """Check if text matches search term using Arabic normalization"""
        normalized_text = cls.normalize_text(text)
        normalized_search = cls.normalize_text(search_term)
        return normalized_search in normalized_text

# Create global instance
arabic_processor = ArabicTextProcessor()

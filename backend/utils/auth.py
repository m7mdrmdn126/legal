from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import hashlib
import platform
from config.settings import settings

# Password hashing context with cross-platform compatibility
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=12  # Explicit rounds for consistency
)

class AuthUtils:
    """Authentication utilities with bcrypt 72-byte limit handling"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt with 72-byte limit handling"""
        try:
            # Convert to bytes to check actual byte length
            password_bytes = password.encode('utf-8')
            
            # If password is longer than 72 bytes, pre-hash with SHA-256
            if len(password_bytes) > 72:
                password = hashlib.sha256(password_bytes).hexdigest()
            
            return pwd_context.hash(password)
        except Exception as e:
            print(f"Error hashing password on {platform.system()}: {e}")
            raise e
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash with bcrypt 72-byte limit handling"""
        try:
            # Convert to bytes to check actual byte length
            password_bytes = plain_password.encode('utf-8')
            
            # If password is longer than 72 bytes, pre-hash with SHA-256
            if len(password_bytes) > 72:
                plain_password = hashlib.sha256(password_bytes).hexdigest()
                
            return pwd_context.verify(plain_password, hashed_password)
        except ValueError as e:
            if "password cannot be longer than 72 bytes" in str(e):
                print(f"Password too long error on {platform.system()}: {e}")
                return False
            print(f"Password verification error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected password verification error on {platform.system()}: {e}")
            return False
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=settings.access_token_expire_hours)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
        """Decode JWT access token"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.PyJWTError:
            return None

# Create global instance
auth_utils = AuthUtils()

from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings
import base64
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None

class EncryptionManager:
    def __init__(self, key: str):
        try:
            # Try to use the key as-is if it's a valid Fernet key
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        except Exception:
            # If not valid, generate a valid key from the string
            key_bytes = key.encode() if isinstance(key, str) else key
            # Create a valid Fernet key by hashing the input
            valid_key = base64.urlsafe_b64encode(
                (key_bytes + b'\x00' * 32)[:32]
            )
            self.cipher = Fernet(valid_key)
    
    def encrypt(self, data: str) -> str:
        try:
            return self.cipher.encrypt(data.encode()).decode()
        except Exception:
            return data
    
    def decrypt(self, encrypted_data: str) -> str:
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception:
            return encrypted_data

encryption_manager = EncryptionManager(settings.encryption_key)


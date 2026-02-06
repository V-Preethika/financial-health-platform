from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from ..models import User
from ..database import get_db
from ..security import hash_password, verify_password, create_access_token, verify_token
from typing import Dict, Any, Optional
from datetime import datetime

router = APIRouter(prefix="/api/auth", tags=["auth"])

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    company_name: str = None
    
    @validator('password')
    def password_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v
    
    @validator('email')
    def email_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Email cannot be empty')
        return v.lower()

class UserLogin(BaseModel):
    email: str
    password: str
    
    @validator('email')
    def email_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Email cannot be empty')
        return v.lower()

class UserUpdate(BaseModel):
    full_name: str = None
    phone: str = None
    company_name: str = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: str = None
    company_name: str = None
    created_at: datetime

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    """Get current user from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    
    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

@router.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Register a new user"""
    
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            company_name=user_data.company_name
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create access token
        access_token = create_access_token(data={"sub": new_user.email, "user_id": new_user.id})
        
        return {
            "status": "success",
            "message": "User registered successfully",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "full_name": new_user.full_name,
                "company_name": new_user.company_name,
                "created_at": new_user.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )

@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Login user"""
    
    try:
        # Find user
        user = db.query(User).filter(User.email == credentials.email).first()
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        
        return {
            "status": "success",
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "company_name": user.company_name,
                "created_at": user.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get current user info"""
    
    return {
        "status": "success",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "company_name": current_user.company_name,
            "created_at": current_user.created_at.isoformat()
        }
    }

@router.post("/logout")
def logout() -> Dict[str, Any]:
    """Logout user"""
    return {
        "status": "success",
        "message": "Logged out successfully"
    }

@router.put("/profile")
def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update user profile"""
    
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    if user_update.phone:
        current_user.phone = user_update.phone
    if user_update.company_name:
        current_user.company_name = user_update.company_name
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "status": "success",
        "message": "Profile updated successfully",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "phone": getattr(current_user, 'phone', None),
            "company_name": current_user.company_name,
            "created_at": current_user.created_at.isoformat()
        }
    }

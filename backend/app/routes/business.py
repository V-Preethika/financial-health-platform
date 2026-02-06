from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..models import Business, BusinessType, User
from .database import get_db
from .security import verify_token
from typing import Dict, Any, List, Optional

router = APIRouter(prefix="/api/businesses", tags=["businesses"])

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

class BusinessCreate(BaseModel):
    business_name: str
    business_type: str
    industry: str
    annual_revenue: float = 0
    employee_count: int = 0
    gst_number: str = None
    pan_number: str = None

class BusinessUpdate(BaseModel):
    business_name: str = None
    industry: str = None
    annual_revenue: float = None
    employee_count: int = None
    gst_number: str = None
    pan_number: str = None

@router.post("/")
async def create_business(
    business: BusinessCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Create a new business"""
    
    # Validate business type
    try:
        business_type = BusinessType[business.business_type.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid business type. Allowed: {[t.value for t in BusinessType]}"
        )
    
    db_business = Business(
        user_id=current_user.id,
        business_name=business.business_name,
        business_type=business_type,
        industry=business.industry,
        annual_revenue=business.annual_revenue,
        employee_count=business.employee_count,
        gst_number=business.gst_number,
        pan_number=business.pan_number
    )
    
    db.add(db_business)
    db.commit()
    db.refresh(db_business)
    
    return {
        "status": "success",
        "message": "Business created successfully",
        "business_id": db_business.id,
        "business": {
            "id": db_business.id,
            "business_name": db_business.business_name,
            "business_type": db_business.business_type.value,
            "industry": db_business.industry,
            "annual_revenue": db_business.annual_revenue,
            "employee_count": db_business.employee_count,
            "created_at": db_business.created_at.isoformat()
        }
    }

@router.get("/")
async def list_businesses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """List all businesses for current user"""
    
    businesses = db.query(Business).filter(Business.user_id == current_user.id).all()
    
    return {
        "status": "success",
        "count": len(businesses),
        "businesses": [
            {
                "id": b.id,
                "business_name": b.business_name,
                "business_type": b.business_type.value,
                "industry": b.industry,
                "annual_revenue": b.annual_revenue,
                "employee_count": b.employee_count,
                "created_at": b.created_at.isoformat()
            }
            for b in businesses
        ]
    }

@router.get("/{business_id}")
async def get_business(
    business_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get business details"""
    
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == current_user.id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    return {
        "status": "success",
        "business": {
            "id": business.id,
            "business_name": business.business_name,
            "business_type": business.business_type.value,
            "industry": business.industry,
            "annual_revenue": business.annual_revenue,
            "employee_count": business.employee_count,
            "gst_number": business.gst_number,
            "pan_number": business.pan_number,
            "created_at": business.created_at.isoformat()
        }
    }

@router.put("/{business_id}")
async def update_business(
    business_id: int,
    business_update: BusinessUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update business details"""
    
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == current_user.id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    if business_update.business_name:
        business.business_name = business_update.business_name
    if business_update.industry:
        business.industry = business_update.industry
    if business_update.annual_revenue is not None:
        business.annual_revenue = business_update.annual_revenue
    if business_update.employee_count is not None:
        business.employee_count = business_update.employee_count
    if business_update.gst_number:
        business.gst_number = business_update.gst_number
    if business_update.pan_number:
        business.pan_number = business_update.pan_number
    
    db.commit()
    db.refresh(business)
    
    return {
        "status": "success",
        "message": "Business updated successfully",
        "business": {
            "id": business.id,
            "business_name": business.business_name,
            "business_type": business.business_type.value,
            "industry": business.industry,
            "annual_revenue": business.annual_revenue,
            "employee_count": business.employee_count,
            "created_at": business.created_at.isoformat()
        }
    }

@router.delete("/{business_id}")
async def delete_business(
    business_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Delete a business"""
    
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == current_user.id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    db.delete(business)
    db.commit()
    
    return {
        "status": "success",
        "message": "Business deleted successfully"
    }

@router.get("/types/list")
async def get_business_types() -> Dict[str, Any]:
    """Get list of supported business types"""
    return {
        "status": "success",
        "business_types": [t.value for t in BusinessType]
    }

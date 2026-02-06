from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from .models import FinancialData, Business, User
from .services.document_processor import DocumentProcessor
from .database import get_db
from .security import verify_token
from typing import Dict, Any, Optional
import json

router = APIRouter(prefix="/api/upload", tags=["upload"])

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

def safe_float(value, default=0):
    """Safely convert value to float"""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except (ValueError, AttributeError):
            return default
    return default

@router.post("/financial-data/{business_id}")
async def upload_financial_data(
    business_id: int,
    file: UploadFile = File(...),
    fiscal_year: str = "2024",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Upload and process financial documents (CSV, XLSX, PDF)"""
    
    # Verify business ownership
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == current_user.id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Read file content
    content = await file.read()
    
    # Process based on file type
    file_ext = file.filename.split('.')[-1].lower()
    financial_data = {}
    expense_breakdown = {}
    
    try:
        if file_ext == 'csv':
            df = DocumentProcessor.process_csv(content)
            financial_data = DocumentProcessor.extract_financial_data(df)
            expense_breakdown = DocumentProcessor.categorize_expenses(df)
        
        elif file_ext in ['xlsx', 'xls']:
            sheets = DocumentProcessor.process_xlsx(content)
            first_sheet = list(sheets.values())[0]
            financial_data = DocumentProcessor.extract_financial_data(first_sheet)
            expense_breakdown = DocumentProcessor.categorize_expenses(first_sheet)
        
        elif file_ext == 'pdf':
            text = DocumentProcessor.process_pdf(content)
            financial_data = {"raw_text": text[:500]}
            expense_breakdown = {}
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV, XLSX, or PDF")
        
        # Safely convert all values to floats
        revenue = safe_float(financial_data.get("revenue"))
        expenses = safe_float(financial_data.get("expenses"))
        net_profit = safe_float(financial_data.get("net_profit"))
        accounts_receivable = safe_float(financial_data.get("accounts_receivable"))
        accounts_payable = safe_float(financial_data.get("accounts_payable"))
        inventory = safe_float(financial_data.get("inventory"))
        total_assets = safe_float(financial_data.get("total_assets"))
        total_liabilities = safe_float(financial_data.get("total_liabilities"))
        equity = safe_float(financial_data.get("equity"))
        
        # Calculate missing values
        if revenue > 0 and expenses > 0 and net_profit == 0:
            net_profit = revenue - expenses
        
        if total_assets == 0 and total_liabilities > 0 and equity > 0:
            total_assets = total_liabilities + equity
        
        # Clean expense breakdown
        clean_expense_breakdown = {}
        for key, value in expense_breakdown.items():
            clean_expense_breakdown[key] = safe_float(value)
        
        # Save to database
        db_financial_data = FinancialData(
            business_id=business_id,
            fiscal_year=fiscal_year,
            revenue=revenue,
            expenses=expenses,
            net_profit=net_profit,
            accounts_receivable=accounts_receivable,
            accounts_payable=accounts_payable,
            inventory=inventory if inventory > 0 else None,
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            equity=equity,
            expense_breakdown=clean_expense_breakdown,
            revenue_streams={}
        )
        
        db.add(db_financial_data)
        db.commit()
        db.refresh(db_financial_data)
        
        return {
            "status": "success",
            "message": "Financial data uploaded successfully",
            "data_id": db_financial_data.id,
            "extracted_data": {
                "revenue": revenue,
                "expenses": expenses,
                "net_profit": net_profit,
                "total_assets": total_assets,
                "total_liabilities": total_liabilities,
                "equity": equity
            },
            "expense_breakdown": clean_expense_breakdown
        }
    
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@router.get("/financial-data/{business_id}")
async def get_financial_data(
    business_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get all financial data for a business"""
    
    # Verify business ownership
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == current_user.id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    financial_records = db.query(FinancialData).filter(
        FinancialData.business_id == business_id
    ).all()
    
    if not financial_records:
        raise HTTPException(status_code=404, detail="No financial data found")
    
    return {
        "status": "success",
        "count": len(financial_records),
        "data": [
            {
                "id": record.id,
                "fiscal_year": record.fiscal_year,
                "revenue": record.revenue,
                "expenses": record.expenses,
                "net_profit": record.net_profit,
                "uploaded_at": record.uploaded_at.isoformat()
            }
            for record in financial_records
        ]
    }

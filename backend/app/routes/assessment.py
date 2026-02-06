from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from ..models import Assessment, FinancialData, Business, User
from ..services.financial_analyzer import FinancialAnalyzer
from ..services.translator import Translator
from ..services.pdf_generator import PDFReportGenerator

from ..database import get_db
from ..security import verify_token
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/assessments", tags=["assessments"])

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

@router.post("/create/{business_id}")
async def create_assessment(
    business_id: int,
    language: str = "en",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Create a financial assessment for a business"""
    
    # Get business and verify ownership
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == current_user.id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Get latest financial data
    financial_data = db.query(FinancialData).filter(
        FinancialData.business_id == business_id
    ).order_by(FinancialData.uploaded_at.desc()).first()
    
    if not financial_data:
        raise HTTPException(status_code=404, detail="No financial data found for this business")
    
    # Prepare financial data dict
    data_dict = {
        "revenue": financial_data.revenue,
        "expenses": financial_data.expenses,
        "net_profit": financial_data.net_profit,
        "accounts_receivable": financial_data.accounts_receivable,
        "accounts_payable": financial_data.accounts_payable,
        "inventory": financial_data.inventory or 0,
        "total_assets": financial_data.total_assets,
        "total_liabilities": financial_data.total_liabilities,
        "equity": financial_data.equity,
        "current_assets": financial_data.total_assets * 0.4,
        "current_liabilities": financial_data.total_liabilities * 0.3,
        "cogs": financial_data.expenses * 0.6,
    }
    
    # Run analysis
    analyzer = FinancialAnalyzer(data_dict, business.business_type)
    assessment_result = analyzer.generate_assessment()
    
    # Save assessment
    assessment = Assessment(
        business_id=business_id,
        user_id=current_user.id,
        assessment_type="comprehensive",
        financial_health_score=assessment_result["financial_health_score"],
        creditworthiness_rating=assessment_result["creditworthiness"]["rating"],
        risk_level=assessment_result["risks"]["risk_level"],
        key_findings=assessment_result["creditworthiness"]["ratios"],
        recommendations=assessment_result["cost_optimizations"],
        cost_optimization_suggestions=assessment_result["cost_optimizations"],
        forecasted_metrics=assessment_result["forecast"],
        industry_benchmarks=assessment_result["benchmarks"]
    )
    
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    # Translate if needed
    if language != "en":
        assessment_result = Translator.translate_dict(assessment_result, language)
    
    return {
        "status": "success",
        "assessment_id": assessment.id,
        "business_id": business_id,
        "assessment": assessment_result,
        "language": language
    }

@router.get("/{assessment_id}")
async def get_assessment(
    assessment_id: int,
    language: str = "en",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get assessment details"""
    
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    result = {
        "id": assessment.id,
        "business_id": assessment.business_id,
        "financial_health_score": assessment.financial_health_score,
        "creditworthiness_rating": assessment.creditworthiness_rating,
        "risk_level": assessment.risk_level,
        "key_findings": assessment.key_findings,
        "recommendations": assessment.recommendations,
        "cost_optimizations": assessment.cost_optimization_suggestions,
        "forecast": assessment.forecasted_metrics,
        "benchmarks": assessment.industry_benchmarks,
        "created_at": assessment.created_at.isoformat()
    }
    
    # Translate if needed
    if language != "en":
        result = Translator.translate_dict(result, language)
    
    return {
        "status": "success",
        "assessment": result,
        "language": language
    }

@router.get("/business/{business_id}")
async def get_business_assessments(
    business_id: int,
    language: str = "en",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get all assessments for a business"""
    
    # Verify business ownership
    business = db.query(Business).filter(
        Business.id == business_id,
        Business.user_id == current_user.id
    ).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    assessments = db.query(Assessment).filter(
        Assessment.business_id == business_id,
        Assessment.user_id == current_user.id
    ).order_by(Assessment.created_at.desc()).all()
    
    if not assessments:
        raise HTTPException(status_code=404, detail="No assessments found")
    
    results = [
        {
            "id": a.id,
            "financial_health_score": a.financial_health_score,
            "creditworthiness_rating": a.creditworthiness_rating,
            "risk_level": a.risk_level,
            "created_at": a.created_at.isoformat()
        }
        for a in assessments
    ]
    
    return {
        "status": "success",
        "count": len(results),
        "assessments": results,
        "language": language
    }

@router.get("/languages/supported")
async def get_supported_languages() -> Dict[str, Any]:
    """Get list of supported languages"""
    return {
        "status": "success",
        "supported_languages": Translator.get_supported_languages()
    }

@router.get("/{assessment_id}/download-pdf")
async def download_assessment_pdf(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download assessment as PDF report"""
    
    # Get assessment
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == current_user.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Get business details
    business = db.query(Business).filter(Business.id == assessment.business_id).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Prepare data for PDF
    assessment_data = {
        "financial_health_score": assessment.financial_health_score,
        "creditworthiness_rating": assessment.creditworthiness_rating,
        "risk_level": assessment.risk_level,
        "key_findings": assessment.key_findings or {},
        "recommendations": assessment.recommendations or [],
        "risks": {"identified_risks": []}  # Parse from recommendations if available
    }
    
    business_data = {
        "business_name": business.business_name,
        "business_type": business.business_type.value,
        "industry": business.industry
    }
    
    # Generate PDF
    pdf_generator = PDFReportGenerator()
    pdf_buffer = pdf_generator.generate_pdf(assessment_data, business_data)
    
    # Return as downloadable file
    filename = f"Assessment_{business.business_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return StreamingResponse(
        iter([pdf_buffer.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

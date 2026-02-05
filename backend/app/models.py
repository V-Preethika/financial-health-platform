from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class BusinessType(str, enum.Enum):
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    AGRICULTURE = "agriculture"
    SERVICES = "services"
    LOGISTICS = "logistics"
    ECOMMERCE = "ecommerce"
    OTHER = "other"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    phone = Column(String, nullable=True)
    company_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    businesses = relationship("Business", back_populates="owner")
    assessments = relationship("Assessment", back_populates="user")

class Business(Base):
    __tablename__ = "businesses"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    business_name = Column(String)
    business_type = Column(Enum(BusinessType))
    industry = Column(String)
    annual_revenue = Column(Float)
    employee_count = Column(Integer)
    gst_number = Column(String, nullable=True)
    pan_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="businesses")
    financial_data = relationship("FinancialData", back_populates="business")
    assessments = relationship("Assessment", back_populates="business")

class FinancialData(Base):
    __tablename__ = "financial_data"
    
    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    fiscal_year = Column(String)
    revenue = Column(Float)
    expenses = Column(Float)
    net_profit = Column(Float)
    cash_flow = Column(Float)
    accounts_receivable = Column(Float)
    accounts_payable = Column(Float)
    inventory = Column(Float, nullable=True)
    total_assets = Column(Float)
    total_liabilities = Column(Float)
    equity = Column(Float)
    expense_breakdown = Column(JSON)  # Category-wise expenses
    revenue_streams = Column(JSON)    # Multiple revenue sources
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    business = relationship("Business", back_populates="financial_data")

class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    business_id = Column(Integer, ForeignKey("businesses.id"))
    assessment_type = Column(String)  # creditworthiness, risk, optimization, etc.
    financial_health_score = Column(Float)
    creditworthiness_rating = Column(String)  # A, B, C, D
    risk_level = Column(String)  # Low, Medium, High
    key_findings = Column(JSON)
    recommendations = Column(JSON)
    cost_optimization_suggestions = Column(JSON)
    forecasted_metrics = Column(JSON)
    industry_benchmarks = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="assessments")
    business = relationship("Business", back_populates="assessments")

class FinancialReport(Base):
    __tablename__ = "financial_reports"
    
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    report_type = Column(String)  # investor, bank, tax, etc.
    language = Column(String, default="en")
    report_content = Column(Text)
    generated_at = Column(DateTime, default=datetime.utcnow)

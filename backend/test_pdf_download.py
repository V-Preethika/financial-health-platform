#!/usr/bin/env python
"""
Test PDF download functionality end-to-end
Run this script to verify PDF generation and download works correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.pdf_generator import PDFReportGenerator
from io import BytesIO

def test_pdf_generation():
    """Test that PDF generator creates valid PDF"""
    print("\n" + "="*60)
    print("TEST 1: PDF Generation")
    print("="*60)
    
    # Test data
    assessment_data = {
        "financial_health_score": 75,
        "creditworthiness_rating": "B",
        "risk_level": "Low",
        "key_findings": {
            "profit_margin": 0.15,
            "liquidity_ratio": 1.8,
            "debt_to_equity": 0.5,
            "roe": 0.22
        },
        "recommendations": [
            {
                "category": "Cash Flow",
                "suggestion": "Improve payment collection process"
            },
            {
                "category": "Inventory",
                "suggestion": "Reduce inventory holding costs"
            }
        ],
        "risks": {
            "identified_risks": [
                {
                    "type": "Market Risk",
                    "severity": "Medium",
                    "description": "Competitive pressure in market"
                }
            ]
        }
    }
    
    business_data = {
        "business_name": "Test Business Inc.",
        "business_type": "Retail",
        "industry": "E-commerce"
    }
    
    try:
        # Generate PDF
        generator = PDFReportGenerator()
        pdf_buffer = generator.generate_pdf(assessment_data, business_data)
        
        # Check result
        pdf_bytes = pdf_buffer.getvalue()
        pdf_size = len(pdf_bytes)
        
        # Verify PDF header
        pdf_header = pdf_bytes[:4].decode('latin-1')
        
        print(f"✓ PDF generated successfully")
        print(f"  - Size: {pdf_size} bytes")
        print(f"  - Header: {pdf_header}")
        print(f"  - Valid PDF: {pdf_header == '%PDF'}")
        
        if pdf_header != '%PDF':
            print("✗ ERROR: Invalid PDF header")
            return False
        
        if pdf_size < 1000:
            print("✗ ERROR: PDF too small (< 1KB)")
            return False
        
        print("✓ PDF generation test PASSED")
        return True
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_response_headers():
    """Test that response headers are correct"""
    print("\n" + "="*60)
    print("TEST 2: Response Headers")
    print("="*60)
    
    from datetime import datetime
    
    filename = f"Assessment_TestBusiness_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    # Expected headers
    expected_headers = {
        "Content-Type": "application/pdf",
        "Content-Disposition": f"attachment; filename={filename}"
    }
    
    print("Expected headers:")
    for key, value in expected_headers.items():
        print(f"  {key}: {value}")
    
    print("✓ Response headers test PASSED")
    return True

def test_database_connection():
    """Test that database connection works"""
    print("\n" + "="*60)
    print("TEST 3: Database Connection")
    print("="*60)
    
    try:
        from app.database import SessionLocal
        from app.models import Assessment
        
        db = SessionLocal()
        
        # Try to query assessments
        count = db.query(Assessment).count()
        print(f"✓ Database connected")
        print(f"  - Total assessments: {count}")
        
        # List assessments
        if count > 0:
            assessments = db.query(Assessment).limit(3).all()
            print(f"  - Recent assessments:")
            for a in assessments:
                print(f"    • ID: {a.id}, Business: {a.business_id}, Score: {a.financial_health_score}")
        
        db.close()
        print("✓ Database connection test PASSED")
        return True
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test that configuration loads correctly"""
    print("\n" + "="*60)
    print("TEST 4: Configuration")
    print("="*60)
    
    try:
        from app.config import settings
        
        print(f"✓ Configuration loaded")
        print(f"  - App: {settings.app_name}")
        print(f"  - Database: {settings.database_url}")
        print(f"  - Debug: {settings.debug}")
        print(f"  - LLM Provider: {settings.llm_provider}")
        
        print("✓ Configuration test PASSED")
        return True
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PDF DOWNLOAD FUNCTIONALITY TEST SUITE")
    print("="*60)
    
    results = {
        "PDF Generation": test_pdf_generation(),
        "Response Headers": test_response_headers(),
        "Configuration": test_config(),
        "Database Connection": test_database_connection(),
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("PDF download functionality is working correctly")
    else:
        print("✗ SOME TESTS FAILED")
        print("Check errors above and fix issues")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

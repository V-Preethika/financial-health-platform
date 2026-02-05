#!/usr/bin/env python
"""
Test PDF download endpoint end-to-end
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_pdf_download():
    """Test complete PDF download flow"""
    print("\n" + "="*60)
    print("PDF DOWNLOAD ENDPOINT TEST")
    print("="*60)
    
    # Step 1: Register user
    print("\n[1] Registering test user...")
    register_data = {
        "email": f"test_{datetime.now().timestamp()}@test.com",
        "password": "testpass123",
        "full_name": "Test User",
        "company_name": "Test Company"
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        print(f"Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Error: {resp.text}")
            return False
        user_data = resp.json()
        print(f"✓ User registered: {user_data.get('user', {}).get('email')}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Step 2: Login
    print("\n[2] Logging in...")
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Error: {resp.text}")
            return False
        login_result = resp.json()
        token = login_result.get("access_token")
        print(f"✓ Logged in, token: {token[:20]}...")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Step 3: Create business
    print("\n[3] Creating business...")
    business_data = {
        "business_name": "Test Business",
        "business_type": "retail",
        "industry": "E-commerce",
        "registration_number": "REG123"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        resp = requests.post(f"{BASE_URL}/api/businesses/", json=business_data, headers=headers)
        print(f"Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Error: {resp.text}")
            return False
        business = resp.json().get("business", {})
        business_id = business.get("id")
        print(f"✓ Business created: ID {business_id}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Step 4: Upload financial data (CSV)
    print("\n[4] Uploading financial data...")
    csv_content = """revenue,expenses,net_profit,accounts_receivable,accounts_payable,inventory,total_assets,total_liabilities,equity
100000,60000,40000,15000,10000,20000,150000,50000,100000"""
    
    try:
        files = {'file': ('financial_data.csv', csv_content)}
        resp = requests.post(
            f"{BASE_URL}/api/upload/financial-data/{business_id}",
            files=files,
            headers=headers
        )
        print(f"Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Error: {resp.text}")
            return False
        print(f"✓ Financial data uploaded")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Step 5: Create assessment
    print("\n[5] Creating assessment...")
    try:
        resp = requests.post(
            f"{BASE_URL}/api/assessments/create/{business_id}",
            headers=headers
        )
        print(f"Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Error: {resp.text}")
            return False
        assessment = resp.json().get("assessment", {})
        assessment_id = resp.json().get("assessment_id")
        print(f"✓ Assessment created: ID {assessment_id}")
        print(f"  - Health Score: {assessment.get('financial_health_score')}")
        print(f"  - Rating: {assessment.get('creditworthiness', {}).get('rating')}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    # Step 6: Download PDF
    print("\n[6] Downloading PDF...")
    try:
        resp = requests.get(
            f"{BASE_URL}/api/assessments/{assessment_id}/download-pdf",
            headers=headers
        )
        print(f"Status: {resp.status_code}")
        print(f"Content-Type: {resp.headers.get('content-type')}")
        print(f"Content-Disposition: {resp.headers.get('content-disposition')}")
        
        if resp.status_code != 200:
            print(f"Error: {resp.text}")
            return False
        
        # Check if response is PDF
        if not resp.headers.get('content-type', '').startswith('application/pdf'):
            print(f"✗ ERROR: Response is not PDF")
            print(f"  Content-Type: {resp.headers.get('content-type')}")
            print(f"  First 100 bytes: {resp.content[:100]}")
            return False
        
        # Check PDF header
        if not resp.content.startswith(b'%PDF'):
            print(f"✗ ERROR: Invalid PDF header")
            print(f"  First 10 bytes: {resp.content[:10]}")
            return False
        
        pdf_size = len(resp.content)
        print(f"✓ PDF downloaded successfully")
        print(f"  - Size: {pdf_size} bytes")
        print(f"  - Header: {resp.content[:4]}")
        
        # Save PDF for inspection
        with open("test_output.pdf", "wb") as f:
            f.write(resp.content)
        print(f"  - Saved to: test_output.pdf")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_download()
    
    print("\n" + "="*60)
    if success:
        print("✓ PDF DOWNLOAD TEST PASSED")
    else:
        print("✗ PDF DOWNLOAD TEST FAILED")
    print("="*60 + "\n")
    
    sys.exit(0 if success else 1)

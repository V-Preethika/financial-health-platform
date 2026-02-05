#!/usr/bin/env python
"""
Verification script to ensure the login fix is working
Run this before starting the servers to confirm everything is ready
"""

import sys
import sqlite3
import os

def check_database():
    """Check if database has correct schema"""
    print("\n=== Checking Database ===")
    db_path = 'financial_health.db'
    
    if not os.path.exists(db_path):
        print(f"✗ Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check users table
    cursor.execute("PRAGMA table_info(users)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    required_columns = ['id', 'email', 'hashed_password', 'full_name', 'company_name', 'created_at', 'phone']
    
    for col in required_columns:
        if col in columns:
            print(f"  ✓ {col}: {columns[col]}")
        else:
            print(f"  ✗ Missing column: {col}")
            conn.close()
            return False
    
    conn.close()
    return True

def check_imports():
    """Check if all required modules can be imported"""
    print("\n=== Checking Imports ===")
    
    modules = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'jose',
        'passlib',
        'cryptography'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module} not installed")
            return False
    
    return True

def check_app():
    """Check if app can be imported"""
    print("\n=== Checking App ===")
    
    try:
        from app.main import app
        print("  ✓ App imports successfully")
        return True
    except Exception as e:
        print(f"  ✗ App import failed: {e}")
        return False

def main():
    print("=" * 50)
    print("FINANCIAL HEALTH PLATFORM - FIX VERIFICATION")
    print("=" * 50)
    
    checks = [
        ("Database Schema", check_database),
        ("Python Imports", check_imports),
        ("FastAPI App", check_app),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Error during {name} check: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("\n✓✓✓ ALL CHECKS PASSED ✓✓✓")
        print("\nYou can now start the servers:")
        print("  Backend:  python -m uvicorn app.main:app --reload")
        print("  Frontend: npm start")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

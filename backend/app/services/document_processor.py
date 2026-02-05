import pandas as pd
import PyPDF2
from typing import Dict, Any, List
import io
import numpy as np

class DocumentProcessor:
    """Handle document uploads and data extraction"""
    
    @staticmethod
    def process_csv(file_content: bytes) -> pd.DataFrame:
        """Process CSV file"""
        return pd.read_csv(io.BytesIO(file_content))
    
    @staticmethod
    def process_xlsx(file_content: bytes) -> Dict[str, pd.DataFrame]:
        """Process Excel file"""
        excel_file = pd.ExcelFile(io.BytesIO(file_content))
        sheets = {}
        for sheet_name in excel_file.sheet_names:
            sheets[sheet_name] = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name)
        return sheets
    
    @staticmethod
    def process_pdf(file_content: bytes) -> str:
        """Extract text from PDF"""
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    
    @staticmethod
    def safe_numeric(value) -> float:
        """Safely convert value to numeric"""
        if pd.isna(value):
            return 0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                # Remove common currency symbols and commas
                cleaned = value.replace('$', '').replace(',', '').replace('₹', '').strip()
                return float(cleaned)
            except (ValueError, AttributeError):
                return 0
        return 0
    
    @staticmethod
    def extract_financial_data(df: pd.DataFrame) -> Dict[str, Any]:
        """Extract financial metrics from dataframe"""
        financial_data = {}
        
        # Common column name variations
        revenue_cols = ["revenue", "sales", "total_revenue", "gross_revenue", "income"]
        expense_cols = ["expenses", "total_expenses", "operating_expenses", "costs"]
        profit_cols = ["net_profit", "profit", "net_income", "earnings", "net earnings"]
        
        # Convert all numeric columns
        for col in df.columns:
            col_lower = col.lower().strip()
            
            # Try to convert column to numeric
            try:
                numeric_col = pd.to_numeric(df[col], errors='coerce')
                col_sum = numeric_col.sum()
                
                if pd.isna(col_sum):
                    continue
                
                col_sum = float(col_sum)
                
                if col_lower in revenue_cols:
                    financial_data["revenue"] = col_sum
                elif col_lower in expense_cols:
                    financial_data["expenses"] = col_sum
                elif col_lower in profit_cols:
                    financial_data["net_profit"] = col_sum
                elif "receivable" in col_lower:
                    financial_data["accounts_receivable"] = col_sum
                elif "payable" in col_lower:
                    financial_data["accounts_payable"] = col_sum
                elif "inventory" in col_lower:
                    financial_data["inventory"] = col_sum
                elif "asset" in col_lower:
                    financial_data["total_assets"] = col_sum
                elif "liability" in col_lower:
                    financial_data["total_liabilities"] = col_sum
                elif "equity" in col_lower or "capital" in col_lower:
                    financial_data["equity"] = col_sum
            except:
                continue
        
        # Calculate missing values
        if "revenue" in financial_data and "expenses" in financial_data:
            if "net_profit" not in financial_data:
                financial_data["net_profit"] = financial_data["revenue"] - financial_data["expenses"]
        
        if "total_assets" not in financial_data and "total_liabilities" in financial_data and "equity" in financial_data:
            financial_data["total_assets"] = financial_data["total_liabilities"] + financial_data["equity"]
        
        # Ensure all values are numeric
        for key in financial_data:
            financial_data[key] = DocumentProcessor.safe_numeric(financial_data[key])
        
        return financial_data
    
    @staticmethod
    def categorize_expenses(df: pd.DataFrame) -> Dict[str, float]:
        """Categorize expenses by type"""
        categories = {}
        
        expense_categories = {
            "salaries": ["salary", "wages", "payroll", "compensation", "employee"],
            "rent": ["rent", "lease", "facility", "premises"],
            "utilities": ["electricity", "water", "gas", "utility", "power"],
            "marketing": ["marketing", "advertising", "promotion", "ads"],
            "supplies": ["supplies", "materials", "inventory", "stock"],
            "maintenance": ["maintenance", "repair", "service", "upkeep"],
            "transportation": ["transport", "shipping", "logistics", "delivery"],
            "other": []
        }
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Skip non-numeric columns
            try:
                numeric_col = pd.to_numeric(df[col], errors='coerce')
                if numeric_col.isna().all():
                    continue
                col_sum = numeric_col.sum()
                if pd.isna(col_sum):
                    continue
                col_sum = float(col_sum)
            except:
                continue
            
            categorized = False
            
            for category, keywords in expense_categories.items():
                if category != "other":
                    for keyword in keywords:
                        if keyword in col_lower:
                            categories[category] = categories.get(category, 0) + col_sum
                            categorized = True
                            break
            
            if not categorized and ("expense" in col_lower or "cost" in col_lower):
                categories["other"] = categories.get("other", 0) + col_sum
        
        return categories

import io
import csv
from typing import Dict, Any, List
from collections import defaultdict
import PyPDF2


class DocumentProcessor:
    """Handle document uploads and data extraction (pandas-free)"""

    @staticmethod
    def process_csv(file_content: bytes) -> List[Dict[str, Any]]:
        """Parse CSV into list of dictionaries"""
        text = file_content.decode("utf-8", errors="ignore")
        reader = csv.DictReader(io.StringIO(text))
        return [row for row in reader]

    @staticmethod
    def process_pdf(file_content: bytes) -> str:
        """Extract text from PDF"""
        reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    @staticmethod
    def safe_numeric(value) -> float:
        """Safely convert value to float"""
        if value is None:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                cleaned = (
                    value.replace(",", "")
                    .replace("$", "")
                    .replace("₹", "")
                    .strip()
                )
                return float(cleaned)
            except ValueError:
                return 0.0
        return 0.0

    @staticmethod
    def extract_financial_data(rows: List[Dict[str, Any]]) -> Dict[str, float]:
        """Extract financial metrics from CSV rows"""
        totals = defaultdict(float)

        revenue_keys = {"revenue", "sales", "income"}
        expense_keys = {"expense", "cost"}
        profit_keys = {"profit", "net_income"}

        for row in rows:
            for key, value in row.items():
                key_l = key.lower().strip()
                amount = DocumentProcessor.safe_numeric(value)

                if any(k in key_l for k in revenue_keys):
                    totals["revenue"] += amount
                elif any(k in key_l for k in expense_keys):
                    totals["expenses"] += amount
                elif any(k in key_l for k in profit_keys):
                    totals["net_profit"] += amount
                elif "receivable" in key_l:
                    totals["accounts_receivable"] += amount
                elif "payable" in key_l:
                    totals["accounts_payable"] += amount
                elif "inventory" in key_l:
                    totals["inventory"] += amount
                elif "asset" in key_l:
                    totals["total_assets"] += amount
                elif "liability" in key_l:
                    totals["total_liabilities"] += amount
                elif "equity" in key_l or "capital" in key_l:
                    totals["equity"] += amount

        # Derivations
        if "net_profit" not in totals and "revenue" in totals and "expenses" in totals:
            totals["net_profit"] = totals["revenue"] - totals["expenses"]

        if "total_assets" not in totals and "total_liabilities" in totals and "equity" in totals:
            totals["total_assets"] = totals["total_liabilities"] + totals["equity"]

        return dict(totals)

    @staticmethod
    def categorize_expenses(rows: List[Dict[str, Any]]) -> Dict[str, float]:
        """Categorize expenses using column names"""
        categories = defaultdict(float)

        mapping = {
            "salaries": ["salary", "wages", "payroll"],
            "rent": ["rent", "lease"],
            "utilities": ["electricity", "water", "gas"],
            "marketing": ["marketing", "ads", "promotion"],
            "supplies": ["supplies", "materials", "inventory"],
            "maintenance": ["maintenance", "repair"],
            "transportation": ["transport", "shipping", "logistics"],
        }

        for row in rows:
            for key, value in row.items():
                key_l = key.lower()
                amount = DocumentProcessor.safe_numeric(value)

                matched = False
                for category, keywords in mapping.items():
                    if any(word in key_l for word in keywords):
                        categories[category] += amount
                        matched = True
                        break

                if not matched and ("expense" in key_l or "cost" in key_l):
                    categories["other"] += amount

        return dict(categories)

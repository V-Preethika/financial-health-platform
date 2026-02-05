from typing import Dict, Any
import json

class Translator:
    """Handle multilingual translations"""
    
    # Translation dictionary
    TRANSLATIONS = {
        "en": {
            "financial_health_score": "Financial Health Score",
            "creditworthiness_rating": "Creditworthiness Rating",
            "risk_level": "Risk Level",
            "revenue": "Revenue",
            "expenses": "Expenses",
            "net_profit": "Net Profit",
            "cash_flow": "Cash Flow",
            "accounts_receivable": "Accounts Receivable",
            "accounts_payable": "Accounts Payable",
            "inventory": "Inventory",
            "total_assets": "Total Assets",
            "total_liabilities": "Total Liabilities",
            "equity": "Equity",
            "low_risk": "Low Risk",
            "medium_risk": "Medium Risk",
            "high_risk": "High Risk",
            "excellent": "Excellent",
            "good": "Good",
            "fair": "Fair",
            "poor": "Poor",
            "key_findings": "Key Findings",
            "recommendations": "Recommendations",
            "cost_optimization": "Cost Optimization Suggestions",
            "industry_benchmarks": "Industry Benchmarks",
            "forecast": "Financial Forecast",
            "revenue_streams": "Revenue Streams",
            "expense_breakdown": "Expense Breakdown",
            "salaries": "Salaries & Wages",
            "rent": "Rent & Facilities",
            "utilities": "Utilities",
            "marketing": "Marketing & Advertising",
            "supplies": "Supplies & Materials",
            "maintenance": "Maintenance & Repairs",
            "transportation": "Transportation & Logistics",
            "other": "Other Expenses",
        },
        "hi": {
            "financial_health_score": "वित्तीय स्वास्थ्य स्कोर",
            "creditworthiness_rating": "साख योग्यता रेटिंग",
            "risk_level": "जोखिम स्तर",
            "revenue": "राजस्व",
            "expenses": "खर्च",
            "net_profit": "शुद्ध लाभ",
            "cash_flow": "नकद प्रवाह",
            "accounts_receivable": "प्राप्य खाते",
            "accounts_payable": "देय खाते",
            "inventory": "सूची",
            "total_assets": "कुल संपत्ति",
            "total_liabilities": "कुल देनदारियां",
            "equity": "इक्विटी",
            "low_risk": "कम जोखिम",
            "medium_risk": "मध्यम जोखिम",
            "high_risk": "उच्च जोखिम",
            "excellent": "उत्कृष्ट",
            "good": "अच्छा",
            "fair": "उचित",
            "poor": "खराब",
            "key_findings": "मुख्य निष्कर्ष",
            "recommendations": "सिफारिशें",
            "cost_optimization": "लागत अनुकूलन सुझाव",
            "industry_benchmarks": "उद्योग बेंचमार्क",
            "forecast": "वित्तीय पूर्वानुमान",
            "revenue_streams": "राजस्व स्रोत",
            "expense_breakdown": "खर्च विवरण",
            "salaries": "वेतन और मजदूरी",
            "rent": "किराया और सुविधाएं",
            "utilities": "उपयोगिताएं",
            "marketing": "विपणन और विज्ञापन",
            "supplies": "आपूर्ति और सामग्री",
            "maintenance": "रखरखाव और मरम्मत",
            "transportation": "परिवहन और रसद",
            "other": "अन्य खर्च",
        }
    }
    
    @staticmethod
    def translate(key: str, language: str = "en") -> str:
        """Translate a key to the specified language"""
        if language not in Translator.TRANSLATIONS:
            language = "en"
        
        return Translator.TRANSLATIONS[language].get(key, key)
    
    @staticmethod
    def translate_dict(data: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
        """Translate all keys in a dictionary"""
        if language not in Translator.TRANSLATIONS:
            language = "en"
        
        translated = {}
        for key, value in data.items():
            translated_key = Translator.translate(key, language)
            
            if isinstance(value, dict):
                translated[translated_key] = Translator.translate_dict(value, language)
            elif isinstance(value, list):
                translated[translated_key] = [
                    Translator.translate_dict(item, language) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                translated[translated_key] = value
        
        return translated
    
    @staticmethod
    def get_supported_languages() -> list:
        """Get list of supported languages"""
        return list(Translator.TRANSLATIONS.keys())

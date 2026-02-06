from typing import Dict, List, Any
from datetime import datetime


class FinancialAnalyzer:
    """Core financial analysis engine"""
    
    INDUSTRY_BENCHMARKS = {
        "manufacturing": {
            "profit_margin": 0.15,
            "debt_to_equity": 1.5,
            "current_ratio": 1.8,
            "inventory_turnover": 6
        },
        "retail": {
            "profit_margin": 0.05,
            "debt_to_equity": 1.0,
            "current_ratio": 1.5,
            "inventory_turnover": 8
        },
        "services": {
            "profit_margin": 0.20,
            "debt_to_equity": 0.8,
            "current_ratio": 2.0,
            "inventory_turnover": 0
        },
        "agriculture": {
            "profit_margin": 0.10,
            "debt_to_equity": 1.2,
            "current_ratio": 1.6,
            "inventory_turnover": 4
        },
        "logistics": {
            "profit_margin": 0.08,
            "debt_to_equity": 1.3,
            "current_ratio": 1.4,
            "inventory_turnover": 12
        },
        "ecommerce": {
            "profit_margin": 0.12,
            "debt_to_equity": 0.9,
            "current_ratio": 1.7,
            "inventory_turnover": 10
        }
    }
    
    def __init__(self, financial_data: Dict[str, Any], business_type: str):
        self.data = financial_data
        self.business_type = business_type.lower()
        self.benchmarks = self.INDUSTRY_BENCHMARKS.get(
            self.business_type,
            self.INDUSTRY_BENCHMARKS["services"]
        )
    
    def calculate_financial_ratios(self) -> Dict[str, float]:
        ratios = {}
        
        revenue = self.data.get("revenue", 0)
        net_profit = self.data.get("net_profit", 0)
        total_assets = self.data.get("total_assets", 1)
        equity = self.data.get("equity", 1)
        
        ratios["profit_margin"] = net_profit / revenue if revenue > 0 else 0
        ratios["roa"] = net_profit / total_assets if total_assets > 0 else 0
        ratios["roe"] = net_profit / equity if equity > 0 else 0
        
        current_assets = self.data.get("current_assets", 0)
        current_liabilities = self.data.get("current_liabilities", 1)
        ratios["current_ratio"] = (
            current_assets / current_liabilities
            if current_liabilities > 0 else 0
        )
        
        total_liabilities = self.data.get("total_liabilities", 0)
        ratios["debt_to_equity"] = (
            total_liabilities / equity if equity > 0 else 0
        )
        ratios["debt_ratio"] = (
            total_liabilities / total_assets if total_assets > 0 else 0
        )
        
        cogs = self.data.get("cogs", 1)
        inventory = self.data.get("inventory", 1)
        ratios["inventory_turnover"] = (
            cogs / inventory if inventory > 0 else 0
        )
        
        accounts_receivable = self.data.get("accounts_receivable", 1)
        ratios["receivables_turnover"] = (
            revenue / accounts_receivable
            if accounts_receivable > 0 else 0
        )
        
        return ratios
    
    def assess_creditworthiness(self) -> Dict[str, Any]:
        ratios = self.calculate_financial_ratios()
        score = 0
        
        profit_margin = ratios.get("profit_margin", 0)
        bm_margin = self.benchmarks["profit_margin"]
        if profit_margin >= bm_margin:
            score += 25
        elif profit_margin >= bm_margin * 0.7:
            score += 15
        elif profit_margin >= 0:
            score += 5
        
        dte = ratios.get("debt_to_equity", 0)
        bm_dte = self.benchmarks["debt_to_equity"]
        if dte <= bm_dte:
            score += 25
        elif dte <= bm_dte * 1.3:
            score += 15
        elif dte <= bm_dte * 1.6:
            score += 5
        
        cr = ratios.get("current_ratio", 0)
        bm_cr = self.benchmarks["current_ratio"]
        if cr >= bm_cr:
            score += 25
        elif cr >= bm_cr * 0.8:
            score += 15
        elif cr >= 1.0:
            score += 5
        
        roe = ratios.get("roe", 0)
        if roe >= 0.15:
            score += 25
        elif roe >= 0.10:
            score += 15
        elif roe >= 0.05:
            score += 5
        
        rating = (
            "A" if score >= 85 else
            "B" if score >= 70 else
            "C" if score >= 55 else
            "D"
        )
        
        return {
            "score": score,
            "rating": rating,
            "ratios": ratios
        }
    
    def identify_risks(self) -> Dict[str, Any]:
        ratios = self.calculate_financial_ratios()
        risks = []
        risk_level = "Low"
        
        if ratios.get("current_ratio", 0) < 1.0:
            risks.append({
                "type": "Liquidity Risk",
                "severity": "High",
                "description": "Current ratio below 1.0"
            })
            risk_level = "High"
        elif ratios.get("current_ratio", 0) < 1.5:
            risks.append({
                "type": "Liquidity Risk",
                "severity": "Medium",
                "description": "Below industry benchmark"
            })
            risk_level = "Medium"
        
        if ratios.get("debt_to_equity", 0) > self.benchmarks["debt_to_equity"] * 1.5:
            risks.append({
                "type": "Solvency Risk",
                "severity": "High",
                "description": "Excessive leverage"
            })
            risk_level = "High"
        
        if ratios.get("profit_margin", 0) < 0:
            risks.append({
                "type": "Profitability Risk",
                "severity": "High",
                "description": "Negative margins"
            })
            risk_level = "High"
        
        return {
            "risk_level": risk_level,
            "identified_risks": risks
        }
    
    def suggest_cost_optimization(self) -> List[Dict[str, Any]]:
        suggestions = []
        ratios = self.calculate_financial_ratios()
        
        if self.data.get("inventory", 0) > 0:
            if ratios.get("inventory_turnover", 0) < self.benchmarks["inventory_turnover"] * 0.8:
                suggestions.append({
                    "category": "Inventory",
                    "action": "Reduce slow-moving stock"
                })
        
        if self.data.get("accounts_receivable", 0) > 0:
            if ratios.get("receivables_turnover", 0) < 8:
                suggestions.append({
                    "category": "Receivables",
                    "action": "Improve collections"
                })
        
        expenses = self.data.get("expenses", 0)
        revenue = self.data.get("revenue", 1)
        if expenses / revenue > 0.85:
            suggestions.append({
                "category": "Expenses",
                "action": "Reduce operating costs"
            })
        
        return suggestions
    
    def forecast_metrics(self, months: int = 12) -> Dict[str, Any]:
        revenue = self.data.get("revenue", 0)
        net_profit = self.data.get("net_profit", 0)
        growth_rate = 0.05
        
        forecast = {
            "forecast_period_months": months,
            "revenue_forecast": [],
            "profit_forecast": []
        }
        
        for month in range(1, months + 1):
            forecast["revenue_forecast"].append({
                "month": month,
                "value": round(revenue * ((1 + growth_rate) ** month), 2)
            })
            forecast["profit_forecast"].append({
                "month": month,
                "value": round(net_profit * ((1 + growth_rate) ** month), 2)
            })
        
        return forecast
    
    def generate_assessment(self) -> Dict[str, Any]:
        credit = self.assess_creditworthiness()
        return {
            "financial_health_score": credit["score"],
            "creditworthiness": credit,
            "risks": self.identify_risks(),
            "cost_optimizations": self.suggest_cost_optimization(),
            "forecast": self.forecast_metrics(),
            "benchmarks": self.benchmarks,
            "assessment_date": datetime.utcnow().isoformat()
        }

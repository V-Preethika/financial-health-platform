import pandas as pd
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta

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
        self.benchmarks = self.INDUSTRY_BENCHMARKS.get(self.business_type, self.INDUSTRY_BENCHMARKS["services"])
    
    def calculate_financial_ratios(self) -> Dict[str, float]:
        """Calculate key financial ratios"""
        ratios = {}
        
        # Profitability Ratios
        revenue = self.data.get("revenue", 0)
        net_profit = self.data.get("net_profit", 0)
        total_assets = self.data.get("total_assets", 1)
        equity = self.data.get("equity", 1)
        
        ratios["profit_margin"] = (net_profit / revenue) if revenue > 0 else 0
        ratios["roa"] = (net_profit / total_assets) if total_assets > 0 else 0
        ratios["roe"] = (net_profit / equity) if equity > 0 else 0
        
        # Liquidity Ratios
        current_assets = self.data.get("current_assets", 0)
        current_liabilities = self.data.get("current_liabilities", 1)
        ratios["current_ratio"] = current_assets / current_liabilities if current_liabilities > 0 else 0
        
        # Leverage Ratios
        total_liabilities = self.data.get("total_liabilities", 0)
        ratios["debt_to_equity"] = (total_liabilities / equity) if equity > 0 else 0
        ratios["debt_ratio"] = (total_liabilities / total_assets) if total_assets > 0 else 0
        
        # Efficiency Ratios
        cogs = self.data.get("cogs", 1)
        inventory = self.data.get("inventory", 1)
        ratios["inventory_turnover"] = (cogs / inventory) if inventory > 0 else 0
        
        accounts_receivable = self.data.get("accounts_receivable", 1)
        ratios["receivables_turnover"] = (revenue / accounts_receivable) if accounts_receivable > 0 else 0
        
        return ratios
    
    def assess_creditworthiness(self) -> Dict[str, Any]:
        """Evaluate creditworthiness and assign rating"""
        ratios = self.calculate_financial_ratios()
        
        score = 0
        max_score = 100
        
        # Profit margin assessment (25 points)
        profit_margin = ratios.get("profit_margin", 0)
        benchmark_margin = self.benchmarks["profit_margin"]
        if profit_margin >= benchmark_margin:
            score += 25
        elif profit_margin >= benchmark_margin * 0.7:
            score += 15
        elif profit_margin >= 0:
            score += 5
        
        # Debt to equity assessment (25 points)
        debt_to_equity = ratios.get("debt_to_equity", 0)
        benchmark_dte = self.benchmarks["debt_to_equity"]
        if debt_to_equity <= benchmark_dte:
            score += 25
        elif debt_to_equity <= benchmark_dte * 1.3:
            score += 15
        elif debt_to_equity <= benchmark_dte * 1.6:
            score += 5
        
        # Current ratio assessment (25 points)
        current_ratio = ratios.get("current_ratio", 0)
        benchmark_cr = self.benchmarks["current_ratio"]
        if current_ratio >= benchmark_cr:
            score += 25
        elif current_ratio >= benchmark_cr * 0.8:
            score += 15
        elif current_ratio >= 1.0:
            score += 5
        
        # ROE assessment (25 points)
        roe = ratios.get("roe", 0)
        if roe >= 0.15:
            score += 25
        elif roe >= 0.10:
            score += 15
        elif roe >= 0.05:
            score += 5
        
        # Assign rating
        if score >= 85:
            rating = "A"
        elif score >= 70:
            rating = "B"
        elif score >= 55:
            rating = "C"
        else:
            rating = "D"
        
        return {
            "score": score,
            "rating": rating,
            "ratios": ratios
        }
    
    def identify_risks(self) -> Dict[str, Any]:
        """Identify financial risks"""
        ratios = self.calculate_financial_ratios()
        risks = []
        risk_level = "Low"
        
        # Check liquidity risk
        if ratios.get("current_ratio", 0) < 1.0:
            risks.append({
                "type": "Liquidity Risk",
                "severity": "High",
                "description": "Current ratio below 1.0 indicates potential difficulty meeting short-term obligations"
            })
            risk_level = "High"
        elif ratios.get("current_ratio", 0) < 1.5:
            risks.append({
                "type": "Liquidity Risk",
                "severity": "Medium",
                "description": "Current ratio below industry benchmark"
            })
            if risk_level == "Low":
                risk_level = "Medium"
        
        # Check solvency risk
        if ratios.get("debt_to_equity", 0) > self.benchmarks["debt_to_equity"] * 1.5:
            risks.append({
                "type": "Solvency Risk",
                "severity": "High",
                "description": "High debt-to-equity ratio indicates excessive leverage"
            })
            risk_level = "High"
        
        # Check profitability risk
        if ratios.get("profit_margin", 0) < 0:
            risks.append({
                "type": "Profitability Risk",
                "severity": "High",
                "description": "Negative profit margin indicates operating losses"
            })
            risk_level = "High"
        elif ratios.get("profit_margin", 0) < self.benchmarks["profit_margin"] * 0.5:
            risks.append({
                "type": "Profitability Risk",
                "severity": "Medium",
                "description": "Profit margin significantly below industry benchmark"
            })
            if risk_level == "Low":
                risk_level = "Medium"
        
        return {
            "risk_level": risk_level,
            "identified_risks": risks
        }
    
    def suggest_cost_optimization(self) -> List[Dict[str, Any]]:
        """Generate cost optimization recommendations"""
        suggestions = []
        ratios = self.calculate_financial_ratios()
        
        # Inventory optimization
        if self.data.get("inventory", 0) > 0:
            inventory_turnover = ratios.get("inventory_turnover", 0)
            benchmark_turnover = self.benchmarks.get("inventory_turnover", 6)
            
            if inventory_turnover < benchmark_turnover * 0.8:
                suggestions.append({
                    "category": "Inventory Management",
                    "suggestion": "Optimize inventory levels",
                    "potential_savings": "5-15% of inventory value",
                    "action": "Implement just-in-time inventory system and reduce slow-moving stock"
                })
        
        # Receivables optimization
        if self.data.get("accounts_receivable", 0) > 0:
            receivables_turnover = ratios.get("receivables_turnover", 0)
            if receivables_turnover < 8:
                suggestions.append({
                    "category": "Receivables Management",
                    "suggestion": "Accelerate cash collection",
                    "potential_savings": "2-5% of receivables",
                    "action": "Implement early payment discounts and stricter credit terms"
                })
        
        # Expense analysis
        expenses = self.data.get("expenses", 0)
        revenue = self.data.get("revenue", 1)
        expense_ratio = expenses / revenue if revenue > 0 else 0
        
        if expense_ratio > 0.85:
            suggestions.append({
                "category": "Operating Expenses",
                "suggestion": "Reduce operating expenses",
                "potential_savings": "5-10% of expenses",
                "action": "Review and optimize overhead costs, negotiate supplier contracts"
            })
        
        return suggestions
    
    def forecast_metrics(self, months: int = 12) -> Dict[str, Any]:
        """Generate financial forecasts"""
        revenue = self.data.get("revenue", 0)
        net_profit = self.data.get("net_profit", 0)
        
        # Simple linear growth forecast (can be enhanced with ML)
        growth_rate = 0.05  # 5% monthly growth assumption
        
        forecast = {
            "forecast_period_months": months,
            "revenue_forecast": [],
            "profit_forecast": []
        }
        
        for month in range(1, months + 1):
            forecasted_revenue = revenue * ((1 + growth_rate) ** month)
            forecasted_profit = net_profit * ((1 + growth_rate) ** month)
            
            forecast["revenue_forecast"].append({
                "month": month,
                "value": round(forecasted_revenue, 2)
            })
            forecast["profit_forecast"].append({
                "month": month,
                "value": round(forecasted_profit, 2)
            })
        
        return forecast
    
    def generate_assessment(self) -> Dict[str, Any]:
        """Generate comprehensive financial assessment"""
        creditworthiness = self.assess_creditworthiness()
        risks = self.identify_risks()
        optimizations = self.suggest_cost_optimization()
        forecast = self.forecast_metrics()
        
        # Calculate health score
        health_score = creditworthiness["score"]
        
        return {
            "financial_health_score": health_score,
            "creditworthiness": creditworthiness,
            "risks": risks,
            "cost_optimizations": optimizations,
            "forecast": forecast,
            "benchmarks": self.benchmarks,
            "assessment_date": datetime.utcnow().isoformat()
        }

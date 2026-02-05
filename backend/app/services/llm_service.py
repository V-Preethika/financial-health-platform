from typing import Dict, Any, Optional
from app.config import settings
import json

class LLMService:
    """Handle LLM interactions for insights and recommendations"""
    
    def __init__(self):
        self.provider = settings.llm_provider
        if self.provider == "openai":
            import openai
            openai.api_key = settings.openai_api_key
            self.client = openai
        elif self.provider == "claude":
            import anthropic
            self.client = anthropic.Anthropic(api_key=settings.claude_api_key)
    
    def generate_insights(self, assessment_data: Dict[str, Any], language: str = "en") -> str:
        """Generate AI-powered insights from assessment data"""
        
        prompt = self._build_insights_prompt(assessment_data, language)
        
        if self.provider == "openai":
            response = self.client.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial analyst providing insights for SMEs."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        
        elif self.provider == "claude":
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
    
    def generate_recommendations(self, assessment_data: Dict[str, Any], language: str = "en") -> list:
        """Generate AI-powered recommendations"""
        
        prompt = self._build_recommendations_prompt(assessment_data, language)
        
        if self.provider == "openai":
            response = self.client.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial advisor providing actionable recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            content = response.choices[0].message.content
        
        elif self.provider == "claude":
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.content[0].text
        
        # Parse recommendations (expecting JSON format)
        try:
            recommendations = json.loads(content)
        except:
            recommendations = [{"recommendation": content}]
        
        return recommendations
    
    def generate_report(self, assessment_data: Dict[str, Any], report_type: str = "investor", language: str = "en") -> str:
        """Generate investor-ready or bank reports"""
        
        prompt = self._build_report_prompt(assessment_data, report_type, language)
        
        if self.provider == "openai":
            response = self.client.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are a professional financial report writer. Generate a {report_type} report."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000
            )
            return response.choices[0].message.content
        
        elif self.provider == "claude":
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
    
    def _build_insights_prompt(self, data: Dict[str, Any], language: str) -> str:
        """Build prompt for insights generation"""
        lang_instruction = "Respond in Hindi" if language == "hi" else "Respond in English"
        
        return f"""
        {lang_instruction}
        
        Analyze the following financial assessment data and provide key insights:
        
        Financial Health Score: {data.get('financial_health_score', 0)}/100
        Creditworthiness Rating: {data.get('creditworthiness', {}).get('rating', 'N/A')}
        Risk Level: {data.get('risks', {}).get('risk_level', 'N/A')}
        
        Key Ratios:
        {json.dumps(data.get('creditworthiness', {}).get('ratios', {}), indent=2)}
        
        Identified Risks:
        {json.dumps(data.get('risks', {}).get('identified_risks', []), indent=2)}
        
        Please provide 3-5 key insights about the financial health of this business.
        """
    
    def _build_recommendations_prompt(self, data: Dict[str, Any], language: str) -> str:
        """Build prompt for recommendations generation"""
        lang_instruction = "Respond in Hindi" if language == "hi" else "Respond in English"
        
        return f"""
        {lang_instruction}
        
        Based on this financial assessment, provide actionable recommendations:
        
        Financial Health Score: {data.get('financial_health_score', 0)}/100
        Risk Level: {data.get('risks', {}).get('risk_level', 'N/A')}
        
        Cost Optimization Opportunities:
        {json.dumps(data.get('cost_optimizations', []), indent=2)}
        
        Please provide 5-7 specific, actionable recommendations prioritized by impact.
        Format as JSON array with fields: priority (1-7), recommendation, expected_impact, timeline
        """
    
    def _build_report_prompt(self, data: Dict[str, Any], report_type: str, language: str) -> str:
        """Build prompt for report generation"""
        lang_instruction = "Respond in Hindi" if language == "hi" else "Respond in English"
        
        report_instructions = {
            "investor": "Focus on growth potential, profitability, and market opportunity",
            "bank": "Focus on creditworthiness, repayment capacity, and collateral value",
            "tax": "Focus on tax compliance, deductions, and regulatory requirements"
        }
        
        instruction = report_instructions.get(report_type, "Provide a comprehensive financial report")
        
        return f"""
        {lang_instruction}
        
        Generate a professional {report_type} report with the following data:
        
        {instruction}
        
        Assessment Data:
        {json.dumps(data, indent=2)}
        
        Format the report with:
        - Executive Summary
        - Financial Overview
        - Key Metrics Analysis
        - Risk Assessment
        - Recommendations
        - Conclusion
        """

llm_service = LLMService()

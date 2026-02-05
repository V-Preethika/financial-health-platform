"""
PDF Report Generator for Financial Assessments
Generates professional PDF reports for business owners and judges
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from io import BytesIO
from typing import Dict, Any

class PDFReportGenerator:
    """Generate professional PDF financial assessment reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Define custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1890ff'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1890ff'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['BodyText'],
            fontSize=11,
            spaceAfter=6,
            leading=14
        ))
    
    def generate_pdf(self, assessment_data: Dict[str, Any], business_data: Dict[str, Any]) -> BytesIO:
        """
        Generate a complete PDF report
        
        Args:
            assessment_data: Assessment results from backend
            business_data: Business information
        
        Returns:
            BytesIO object containing PDF
        """
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Title Page
        story.extend(self._create_title_page(business_data, assessment_data))
        story.append(PageBreak())
        
        # Executive Summary
        story.extend(self._create_executive_summary(assessment_data, business_data))
        story.append(PageBreak())
        
        # Financial Health Scores
        story.extend(self._create_scores_section(assessment_data))
        story.append(PageBreak())
        
        # Risk Assessment
        story.extend(self._create_risk_section(assessment_data))
        story.append(PageBreak())
        
        # Recommendations
        story.extend(self._create_recommendations_section(assessment_data))
        story.append(PageBreak())
        
        # Key Findings
        story.extend(self._create_key_findings_section(assessment_data))
        
        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer
    
    def _create_title_page(self, business_data: Dict, assessment_data: Dict) -> list:
        """Create title page"""
        story = []
        
        story.append(Spacer(1, 1.5*inch))
        
        # Main title
        story.append(Paragraph(
            "Financial Health Assessment Report",
            self.styles['CustomTitle']
        ))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Business name
        story.append(Paragraph(
            f"<b>{business_data.get('business_name', 'N/A')}</b>",
            ParagraphStyle(
                'BusinessName',
                parent=self.styles['Normal'],
                fontSize=16,
                alignment=TA_CENTER,
                spaceAfter=12
            )
        ))
        
        # Business type and industry
        story.append(Paragraph(
            f"{business_data.get('business_type', 'N/A')} | {business_data.get('industry', 'N/A')}",
            ParagraphStyle(
                'BusinessInfo',
                parent=self.styles['Normal'],
                fontSize=12,
                alignment=TA_CENTER,
                textColor=colors.grey,
                spaceAfter=24
            )
        ))
        
        story.append(Spacer(1, 0.5*inch))
        
        # Report metadata
        metadata_style = ParagraphStyle(
            'Metadata',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        
        story.append(Paragraph(
            f"Report Generated: {datetime.now().strftime('%B %d, %Y')}",
            metadata_style
        ))
        
        story.append(Paragraph(
            "Confidential - For Authorized Use Only",
            ParagraphStyle(
                'Confidential',
                parent=self.styles['Normal'],
                fontSize=9,
                alignment=TA_CENTER,
                textColor=colors.red,
                spaceAfter=12
            )
        ))
        
        return story
    
    def _create_executive_summary(self, assessment_data: Dict, business_data: Dict) -> list:
        """Create executive summary section"""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        # Summary text
        health_score = assessment_data.get('financial_health_score', 0)
        rating = assessment_data.get('creditworthiness_rating', 'N/A')
        risk_level = assessment_data.get('risk_level', 'N/A')
        
        summary_text = f"""
        This report provides a comprehensive financial health assessment for <b>{business_data.get('business_name')}</b>.
        The assessment evaluates creditworthiness, financial stability, and operational efficiency based on submitted 
        financial data. The business has achieved a financial health score of <b>{health_score}/100</b> with a 
        creditworthiness rating of <b>{rating}</b> and identified risk level of <b>{risk_level}</b>.
        <br/><br/>
        Key highlights and recommendations are detailed in the following sections.
        """
        
        story.append(Paragraph(summary_text, self.styles['CustomBodyText']))
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _create_scores_section(self, assessment_data: Dict) -> list:
        """Create financial scores section"""
        story = []
        
        story.append(Paragraph("Financial Health Scores", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        # Scores table
        health_score = assessment_data.get('financial_health_score', 0)
        rating = assessment_data.get('creditworthiness_rating', 'N/A')
        risk_level = assessment_data.get('risk_level', 'N/A')
        
        scores_data = [
            ['Metric', 'Score', 'Interpretation'],
            ['Financial Health Score', f'{health_score}/100', self._get_health_interpretation(health_score)],
            ['Creditworthiness Rating', rating, self._get_rating_interpretation(rating)],
            ['Risk Level', risk_level, self._get_risk_interpretation(risk_level)]
        ]
        
        scores_table = Table(scores_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1890ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
        ]))
        
        story.append(scores_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Score explanations
        story.append(Paragraph("<b>Score Explanations:</b>", self.styles['CustomBodyText']))
        
        explanations = [
            f"<b>Financial Health Score ({health_score}/100):</b> Measures overall financial stability and operational efficiency.",
            f"<b>Creditworthiness Rating ({rating}):</b> Indicates ability to repay debt. A=Excellent, B=Good, C=Fair, D=Poor.",
            f"<b>Risk Level ({risk_level}):</b> Assesses financial vulnerability. Low=Stable, Medium=Monitor, High=Critical."
        ]
        
        for explanation in explanations:
            story.append(Paragraph(explanation, self.styles['CustomBodyText']))
            story.append(Spacer(1, 0.05*inch))
        
        return story
    
    def _create_risk_section(self, assessment_data: Dict) -> list:
        """Create risk assessment section"""
        story = []
        
        story.append(Paragraph("Risk Assessment", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        risks = assessment_data.get('risks', {}).get('identified_risks', [])
        
        if risks:
            for idx, risk in enumerate(risks[:5], 1):  # Limit to top 5 risks
                severity = risk.get('severity', 'Medium')
                risk_type = risk.get('type', 'Unknown')
                description = risk.get('description', 'No description')
                
                # Risk item with severity indicator
                risk_text = f"""
                <b>{idx}. {risk_type}</b> <font color="{self._get_severity_color(severity)}">[{severity}]</font><br/>
                {description}
                """
                story.append(Paragraph(risk_text, self.styles['CustomBodyText']))
                story.append(Spacer(1, 0.1*inch))
        else:
            story.append(Paragraph(
                "✓ No significant risks identified. Business shows stable financial health.",
                ParagraphStyle(
                    'GoodNews',
                    parent=self.styles['CustomBodyText'],
                    textColor=colors.HexColor('#52c41a')
                )
            ))
        
        story.append(Spacer(1, 0.1*inch))
        return story
    
    def _create_recommendations_section(self, assessment_data: Dict) -> list:
        """Create recommendations section"""
        story = []
        
        story.append(Paragraph("Recommendations", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        recommendations = assessment_data.get('recommendations', [])
        
        if recommendations:
            for idx, rec in enumerate(recommendations[:5], 1):  # Limit to top 5
                category = rec.get('category', 'General')
                suggestion = rec.get('suggestion', 'No suggestion')
                
                rec_text = f"<b>{idx}. {category}:</b> {suggestion}"
                story.append(Paragraph(rec_text, self.styles['CustomBodyText']))
                story.append(Spacer(1, 0.08*inch))
        else:
            story.append(Paragraph(
                "No specific recommendations at this time.",
                self.styles['CustomBodyText']
            ))
        
        story.append(Spacer(1, 0.1*inch))
        return story
    
    def _create_key_findings_section(self, assessment_data: Dict) -> list:
        """Create key findings section"""
        story = []
        
        story.append(Paragraph("Key Financial Ratios", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        key_findings = assessment_data.get('key_findings', {})
        
        if key_findings:
            findings_data = [['Ratio', 'Value']]
            for key, value in list(key_findings.items())[:6]:  # Limit to 6 ratios
                findings_data.append([
                    key.replace('_', ' ').title(),
                    f'{value:.2f}' if isinstance(value, (int, float)) else str(value)
                ])
            
            findings_table = Table(findings_data, colWidths=[3*inch, 2*inch])
            findings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1890ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
            ]))
            
            story.append(findings_table)
        else:
            story.append(Paragraph("No key findings available.", self.styles['CustomBodyText']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_text = """
        <font size=8 color="grey">
        This report is confidential and intended for authorized use only. 
        The information contained herein is based on data provided and analysis performed at the time of assessment.
        </font>
        """
        story.append(Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey
        )))
        
        return story
    
    @staticmethod
    def _get_health_interpretation(score: float) -> str:
        """Get interpretation for health score"""
        if score >= 80:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 60:
            return "Fair"
        else:
            return "Poor"
    
    @staticmethod
    def _get_rating_interpretation(rating: str) -> str:
        """Get interpretation for creditworthiness rating"""
        interpretations = {
            'A': 'Excellent creditworthiness',
            'B': 'Good creditworthiness',
            'C': 'Fair creditworthiness',
            'D': 'Poor creditworthiness'
        }
        return interpretations.get(rating, 'Unknown')
    
    @staticmethod
    def _get_risk_interpretation(risk_level: str) -> str:
        """Get interpretation for risk level"""
        interpretations = {
            'Low': 'Stable financial position',
            'Medium': 'Monitor closely',
            'High': 'Critical attention needed'
        }
        return interpretations.get(risk_level, 'Unknown')
    
    @staticmethod
    def _get_severity_color(severity: str) -> str:
        """Get color for risk severity"""
        colors_map = {
            'Low': '#52c41a',
            'Medium': '#faad14',
            'High': '#ff4d4f'
        }
        return colors_map.get(severity, '#1890ff')

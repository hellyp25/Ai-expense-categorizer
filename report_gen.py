import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

class ReportGenerator:
    @staticmethod
    def generate_pdf(df: pd.DataFrame, insights: dict) -> io.BytesIO:
        """Compiles clean balance reports into a downloadable PDF format."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=20)
        h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=16, spaceBefore=15, spaceAfter=10)
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=11, leading=14)

        # Title Block
        story.append(Paragraph("AI Financial Assistant Executive Report", title_style))
        story.append(Spacer(1, 10))
        
        # Summary Segment
        story.append(Paragraph(f"<b>Financial Health Score:</b> {insights.get('financial_health_score', 'N/A')}/100", body_style))
        story.append(Paragraph(f"<b>Executive Summary:</b> {insights.get('spending_habits_summary', '')}", body_style))
        story.append(Spacer(1, 15))
        
        # Table of Transactions
        story.append(Paragraph("Categorized Transaction Logs", h2_style))
        table_data = [["Date", "Description", "Amount", "Category"]]
        for _, row in df.head(30).iterrows():  # Cap page overflow length for preview limits
            table_data.append([
                row['Date'].strftime('%Y-%m-%d'),
                row['Description'][:30],
                f"${row['Amount']:.2f}",
                row['Category']
            ])
            
        t = Table(table_data, colWidths=[80, 220, 80, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.beige, colors.white]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ]))
        story.append(t)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
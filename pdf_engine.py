from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from datetime import datetime

class PDFGenerator:
    def __init__(self):
        print("📄 Initializing PDF Engine...")

    def generate_report(self, data, filename="TIE_Report.pdf"):
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()

            # --- HEADER ---
            title_style = styles['Title']
            title_style.textColor = colors.HexColor("#4f46e5")
            story.append(Paragraph("TIE: Teacher Insight Engine Report", title_style))
            story.append(Spacer(1, 0.2 * inch))

            # --- METADATA ---
            date_str = datetime.now().strftime("%b %d, %Y - %H:%M %p")
            overall = str(data.get("overall_score", "0"))
            
            meta_data = [
                ["Session Date:", date_str],
                ["Overall Score:", f"{overall}/100"],
                ["Performance Tier:", self._get_tier(int(overall) if overall.isdigit() else 0)]
            ]
            
            meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
            meta_table.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor("#334155")),
                ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 0.3 * inch))

            # --- METRICS ---
            story.append(Paragraph("Detailed Metrics", styles['Heading2']))
            
            clarity = str(data.get("clarity", {}).get("clarity_score", "0"))
            interaction = str(data.get("interaction", {}).get("interaction_ratio_percent", "0"))
            vocal = str(data.get("vocal", {}).get("avg_pitch", "0"))
            eye = str(data.get("video", {}).get("eye_contact_score", "0"))
            
            metrics_data = [
                ['Metric', 'Score', 'Status'],
                ['Content Clarity', f"{clarity}%", self._get_status(clarity)],
                ['Interaction Ratio', f"{interaction}%", "Active" if float(interaction) > 20 else "Low"],
                ['Visual Engagement', f"{eye}%", "Good" if float(eye) > 50 else "Needs Focus"],
                ['Vocal Pitch', f"{int(float(vocal))} Hz", data.get("vocal", {}).get("delivery_status", "Normal")]
            ]

            metric_table = Table(metrics_data, colWidths=[2.5*inch, 1.5*inch, 2.5*inch])
            metric_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e0e7ff")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#3730a3")),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#e2e8f0")),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ]))
            story.append(metric_table)
            
            # --- FEEDBACK ---
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph("AI Neural Feedback", styles['Heading2']))
            feedback = data.get("clarity", {}).get("feedback", "No specific feedback generated.")
            story.append(Paragraph(f"<b>Analysis:</b> {feedback}", styles['Normal']))

            doc.build(story)
            print("✅ PDF Generated Successfully!")
            
        except Exception as e:
            print(f"❌ PDF Engine Error: {e}")
            raise e

    def _get_tier(self, score):
        if score >= 80: return "Excellent"
        if score >= 60: return "Good Progress"
        return "Needs Optimization"

    def _get_status(self, score):
        try:
            return "Strong" if float(score) > 75 else "Average"
        except:
            return "N/A"
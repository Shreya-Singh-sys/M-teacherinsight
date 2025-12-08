from fpdf import FPDF
import datetime

class PDFReport(FPDF):
    def header(self):
        # Logo or Title
        self.set_font('Arial', 'B', 16)
        self.set_text_color(79, 70, 229) # Indigo Color
        self.cell(0, 10, 'TIE - Teacher Insight Engine', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

class ReportGenerator:
    def generate_pdf(self, data, filename="TIE_Report.pdf"):
        pdf = PDFReport()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # --- 1. SESSION INFO ---
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, f"Session Analysis Report", 0, 1)
        
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 6, f"Date: {datetime.date.today()}", 0, 1)
        pdf.cell(0, 6, f"Overall Score: {data.get('overall_score', 'N/A')}/100", 0, 1)
        pdf.ln(10)

        # --- 2. KEY METRICS TABLE ---
        # Header
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(90, 8, "Metric", 1, 0, 'L', True)
        pdf.cell(40, 8, "Score", 1, 0, 'C', True)
        pdf.cell(60, 8, "Status", 1, 1, 'C', True)

        # Data Rows
        pdf.set_font("Arial", '', 10)
        
        # Helper to safely get data
        def get_row(metric, score, status):
            pdf.cell(90, 8, metric, 1)
            pdf.cell(40, 8, str(score), 1, 0, 'C')
            pdf.cell(60, 8, status, 1, 1, 'C')

        # Extract values safely
        clarity_score = data.get('clarity', {}).get('clarity_score', 0)
        inter_score = data.get('interaction', {}).get('interaction_ratio_percent', 0)
        eye_score = data.get('video', {}).get('eye_contact_score', 0)
        vocal_hz = data.get('vocal', {}).get('avg_pitch', 0)

        get_row("Content Clarity", f"{clarity_score}%", "Excellent" if clarity_score > 75 else "Needs Work")
        get_row("Student Interaction", f"{inter_score}%", "Interactive" if inter_score > 20 else "Low")
        get_row("Visual Eye Contact", f"{eye_score}%", "Good" if eye_score > 50 else "Poor")
        get_row("Vocal Pitch (Avg)", f"{int(vocal_hz)} Hz", data.get('vocal', {}).get('delivery_status', 'Normal'))
        
        pdf.ln(10)

        # --- 3. DETAILED AI FEEDBACK ---
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Detailed AI Insights", 0, 1)
        
        pdf.set_font("Arial", '', 10)
        # Content Feedback
        feedback_text = data.get('clarity', {}).get('feedback', 'No detailed feedback available.')
        # Clean up text (FPDF doesn't support some unicode characters)
        feedback_text = feedback_text.encode('latin-1', 'replace').decode('latin-1')
        
        pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(0, 6, f"AI Feedback: {feedback_text}")
        
        # --- 4. ACTION PLAN ---
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, "Recommended Action Plan:", 0, 1)
        pdf.set_font("Arial", 'I', 10)
        
        if clarity_score < 60:
            plan = "- Review key terms before class to reduce jargon usage."
        elif inter_score < 10:
            plan = "- Incorporate a Q&A session every 15 minutes."
        else:
            plan = "- Maintain current teaching pace and style."
            
        pdf.multi_cell(0, 6, plan)

        # Output
        pdf.output(filename)
        return filename
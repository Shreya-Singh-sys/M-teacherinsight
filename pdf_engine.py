from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from datetime import datetime

class PDFGenerator:
    """
    PDF Report Generator
    --------------------
    Current: Local PDF generation using ReportLab
    Azure-ready: Can be extended to store reports in Azure Blob Storage
                 or share via email / dashboard download
    """

    def __init__(self):
        print("📄 Initializing PDF Engine...")

    def generate_report(self, data, filename="TIE_Report.pdf"):
        """
        Generates a professional PDF report from analysis data.
        data: Dictionary containing analysis results
        filename: Output file path
        """
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()

            # --------------------------------------------------
            # 1. TITLE SECTION
            # --------------------------------------------------
            title_style = styles["Title"]
            title_style.textColor = colors.HexColor("#4f46e5")  # Indigo Blue

            story.append(
                Paragraph("TIE: Teacher Insight Engine Report", title_style)
            )
            story.append(Spacer(1, 0.2 * inch))

            # --------------------------------------------------
            # 2. METADATA TABLE
            # --------------------------------------------------
            date_str = datetime.now().strftime("%b %d, %Y - %H:%M %p")
            overall = str(data.get("overall_score", "0"))

            # Determine performance tier
            try:
                score_int = int(float(overall))
                if score_int >= 80:
                    tier = "Excellent"
                elif score_int >= 60:
                    tier = "Good Progress"
                else:
                    tier = "Needs Optimization"
            except Exception:
                tier = "N/A"

            meta_data = [
                ["Session Date:", date_str],
                ["Overall Score:", f"{overall}/100"],
                ["Performance Tier:", tier],
            ]

            meta_table = Table(meta_data, colWidths=[2.5 * inch, 3.5 * inch])
            meta_table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#334155")),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ]
                )
            )

            story.append(meta_table)
            story.append(Spacer(1, 0.3 * inch))

            # --------------------------------------------------
            # 3. DETAILED METRICS
            # --------------------------------------------------
            story.append(
                Paragraph("Detailed Performance Metrics", styles["Heading2"])
            )

            clarity = str(data.get("clarity", {}).get("clarity_score", "0"))
            interaction = str(
                data.get("interaction", {}).get("interaction_ratio_percent", "0")
            )
            vocal = str(data.get("vocal", {}).get("avg_pitch", "0"))
            eye = str(data.get("video", {}).get("eye_contact_score", "0"))

            metrics_data = [
                ["Metric Category", "Score / Value", "Assessment"],
                [
                    "Content Clarity",
                    f"{clarity}%",
                    "Strong" if float(clarity) > 75 else "Average",
                ],
                [
                    "Interaction Ratio",
                    f"{interaction}%",
                    "Active" if float(interaction) > 20 else "Low",
                ],
                [
                    "Visual Engagement",
                    f"{eye}%",
                    "Good Focus" if float(eye) > 50 else "Needs Improvement",
                ],
                [
                    "Vocal Pitch",
                    f"{int(float(vocal))} Hz",
                    data.get("vocal", {}).get("delivery_status", "Normal"),
                ],
            ]

            metric_table = Table(
                metrics_data, colWidths=[2.5 * inch, 1.5 * inch, 2.5 * inch]
            )
            metric_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0e7ff")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#3730a3")),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ]
                )
            )

            story.append(metric_table)

            # --------------------------------------------------
            # 4. AI FEEDBACK SECTION
            # --------------------------------------------------
            story.append(Spacer(1, 0.4 * inch))
            story.append(Paragraph("AI Neural Feedback", styles["Heading2"]))

            feedback_text = data.get("clarity", {}).get(
                "feedback", "No specific feedback generated for this session."
            )
            feedback_text = str(feedback_text).replace("<", "&lt;").replace(">", "&gt;")

            story.append(
                Paragraph(
                    f"<b>Primary Observation:</b> {feedback_text}",
                    styles["Normal"],
                )
            )

            # --------------------------------------------------
            # FOOTER
            # --------------------------------------------------
            story.append(Spacer(1, 0.5 * inch))
            footer_style = styles["Italic"]
            footer_style.textColor = colors.HexColor("#94a3b8")

            story.append(
                Paragraph(
                    "Generated by Teacher Insight Engine (TIE). Automated Analysis.",
                    footer_style,
                )
            )

            # Build PDF
            doc.build(story)
            print(f"✅ PDF Generated Successfully at: {filename}")

        except Exception as e:
            print(f"❌ PDF Generation Failed: {e}")
            # Fail silently (do not crash backend)

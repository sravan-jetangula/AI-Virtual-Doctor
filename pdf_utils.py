from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io

def create_prescription_pdf(patient, text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>AI Doctor Prescription</b>", styles["Title"]))
    story.append(Paragraph(text.replace("\n", "<br/>"), styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer

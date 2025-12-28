
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(text):
    path="prescription.pdf"
    doc=SimpleDocTemplate(path)
    styles=getSampleStyleSheet()
    doc.build([Paragraph(t,styles["Normal"]) for t in text.split("\n")])
    return path

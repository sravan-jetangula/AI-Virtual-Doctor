import os, uuid, sqlite3, tempfile
import streamlit as st
import speech_recognition as sr
from groq import Groq
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from datetime import datetime

# ================= PAGE CONFIG =================
st.set_page_config(page_title="AI Virtual Doctor", page_icon="🩺", layout="wide")

# ================= CSS =================
st.markdown("""
<style>
body { background-color: #f5f9ff; }
.patient-card, .chat-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}
.arrow-btn button {
    border-radius: 50%;
    width: 44px;
    height: 44px;
    font-size: 20px;
    background-color: #1565c0;
    color: white;
    border: none;
}
.arrow-btn button:hover {
    background-color: #0d47a1;
}
</style>
""", unsafe_allow_html=True)

# ================= GROQ =================
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    st.error("❌ GROQ_API_KEY not set")
    st.stop()

client = Groq(api_key=API_KEY)

# ================= DATABASE =================
conn = sqlite3.connect("patients.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS patients(
id TEXT PRIMARY KEY,
name TEXT, age INT, gender TEXT,
phone TEXT, weight TEXT, allergy TEXT, language TEXT
)
""")
conn.commit()

# ================= SESSION =================
st.session_state.setdefault("page", "welcome")
st.session_state.setdefault("chat", [])
st.session_state.setdefault("final_rx", None)
st.session_state.setdefault("show_patient", True)
st.session_state.setdefault("uploads", [])
st.session_state.setdefault("last_voice_text", "")

# ================= VOICE =================
def voice_to_text(audio, lang):
    r = sr.Recognizer()
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(audio.read())
        path = f.name
    with sr.AudioFile(path) as src:
        data = r.record(src)
    return r.recognize_google(
        data,
        language={"English":"en-IN","Hindi":"hi-IN","Telugu":"te-IN"}.get(lang,"en-IN")
    )

# ================= PDF =================
def create_pdf(patient, rx):
    file = "Prescription.pdf"
    doc = SimpleDocTemplate(file, pagesize=A4,
        rightMargin=2*cm,leftMargin=2*cm,topMargin=2*cm,bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>AI VIRTUAL DOCTOR – PRESCRIPTION</b>", styles["Title"]))
    story.append(Spacer(1,12))
    story.append(Paragraph(
        f"<b>Name:</b> {patient[1]}<br/>"
        f"<b>Age/Gender:</b> {patient[2]} / {patient[3]}<br/>"
        f"<b>Phone:</b> {patient[4]}<br/>"
        f"<b>Weight:</b> {patient[5]} kg<br/>"
        f"<b>Date:</b> {datetime.now().strftime('%d-%b-%Y')}",
        styles["Normal"]
    ))
    story.append(Spacer(1,12))

    for block in rx.split("\n\n"):
        story.append(Paragraph(block.replace("\n","<br/>"), styles["Normal"]))
        story.append(Spacer(1,10))

    story.append(Spacer(1,20))
    story.append(Paragraph("<b>Doctor Signature</b><br/>AI Virtual Doctor", styles["Normal"]))
    doc.build(story)
    return file

# ================= AI =================
def doctor_ai(text, patient, lang):
    prompt = f"""
You are a professional medical doctor.
Ask ONE question at a time.
Ask follow-ups dynamically.
When enough data is collected, give FINAL PRESCRIPTION.

Language: {lang}
Patient: {patient[1]}, {patient[2]} years, {patient[3]}
"""
    messages = [{"role":"system","content":prompt}] + st.session_state.chat
    messages.append({"role":"user","content":text})

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.2,
        max_tokens=700
    )

    reply = res.choices[0].message.content.strip()
    if "FINAL PRESCRIPTION" in reply.upper():
        st.session_state.final_rx = reply
    return reply

# ================= FLOW =================
# (Welcome + Register unchanged — already correct)

# ================= CONSULT =================
# ONLY CHANGE IS VOICE HANDLING BELOW 👇

# inside chat section replace voice block with:

# ---- VOICE SAFE HANDLING ----
if audio:
    try:
        voice_text = voice_to_text(audio, st.session_state.language)
        if voice_text.strip().lower() != st.session_state.last_voice_text.lower():
            user_text = voice_text
            st.session_state.last_voice_text = voice_text
        else:
            user_text = None
    except:
        st.warning("Voice unclear, please speak again")
        user_text = None

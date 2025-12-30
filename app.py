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
.patient-card,.chat-card{
background:white;padding:15px;border-radius:14px;
box-shadow:0 4px 10px rgba(0,0,0,.08)
}
</style>
""", unsafe_allow_html=True)

# ================= GROQ =================
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    st.error("GROQ_API_KEY missing")
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
st.session_state.setdefault("final_rx", "")
st.session_state.setdefault("show_patient", True)
st.session_state.setdefault("last_audio_id", None)

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
def create_pdf(patient, rx_text):
    file = "Prescription.pdf"
    doc = SimpleDocTemplate(
        file, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>AI VIRTUAL DOCTOR – PRESCRIPTION</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"""
<b>Patient Details</b><br/>
Name: {patient[1]}<br/>
Age / Gender: {patient[2]} / {patient[3]}<br/>
Phone: {patient[4]}<br/>
Weight: {patient[5]} kg<br/>
Allergy: {patient[6]}<br/>
Date: {datetime.now().strftime('%d %b %Y')}
""", styles["Normal"]))

    story.append(Spacer(1, 14))

    for section in rx_text.split("\n\n"):
        story.append(Paragraph(section.replace("\n", "<br/>"), styles["Normal"]))
        story.append(Spacer(1, 10))

    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Doctor Signature</b><br/>AI Virtual Doctor", styles["Normal"]))

    doc.build(story)
    return file

# ================= AI =================
def doctor_ai(text, patient, lang):
    prompt = f"""
You are a professional medical doctor.
Ask ONE relevant question at a time.
When enough info is collected, provide a LONG FINAL PRESCRIPTION.

Include:
• Symptoms summary
• Probable diagnosis
• Medicines
• Home remedies
• Lifestyle advice
• Warning signs

Language: {lang}
Patient: {patient[1]}, {patient[2]} years, {patient[3]}
"""

    messages = [{"role": "system", "content": prompt}] + st.session_state.chat
    messages.append({"role": "user", "content": text})

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.25,
        max_tokens=900
    )

    reply = res.choices[0].message.content.strip()

    if "FINAL PRESCRIPTION" in reply.upper():
        st.session_state.final_rx = reply

    return reply

# ================= WELCOME =================
if st.session_state.page == "welcome":
    st.markdown("""
<div style="background:linear-gradient(135deg,#1565c0,#42a5f5);
padding:60px;border-radius:25px;color:white;text-align:center;">
<h1>🩺 AI Virtual Doctor</h1>
<p>Professional AI-powered medical guidance</p>
</div>
""", unsafe_allow_html=True)

    if st.button("🚀 Start Consultation", use_container_width=True):
        st.session_state.page = "register"
        st.rerun()

# ================= REGISTER =================
elif st.session_state.page == "register":
    st.header("📝 Patient Registration")

    name = st.text_input("Name")
    age = st.number_input("Age", 1, 120)
    gender = st.selectbox("Gender", ["Male", "Female"])
    phone = st.text_input("Phone")
    weight = st.text_input("Weight")
    allergy = st.text_input("Allergy")
    lang = st.selectbox("Language", ["English", "Hindi", "Telugu"])

    if st.button("Proceed"):
        pid = str(uuid.uuid4())[:8]
        c.execute(
            "INSERT INTO patients VALUES (?,?,?,?,?,?,?,?)",
            (pid, name, age, gender, phone, weight, allergy, lang)
        )
        conn.commit()
        st.session_state.pid = pid
        st.session_state.language = lang
        st.session_state.page = "consult"
        st.rerun()

# ================= CONSULT =================
else:
    c.execute("SELECT * FROM patients WHERE id=?", (st.session_state.pid,))
    patient = c.fetchone()

    if st.button("<<" if st.session_state.show_patient else ">>"):
        st.session_state.show_patient = not st.session_state.show_patient
        st.rerun()

    if st.session_state.show_patient:
        left, right = st.columns([1.3, 3.7])
    else:
        right = st.container()

    if st.session_state.show_patient:
        with left:
            st.markdown("<div class='patient-card'>", unsafe_allow_html=True)
            st.subheader("👤 Patient Information")
            st.write(f"**Name:** {patient[1]}")
            st.write(f"**Age:** {patient[2]}")
            st.write(f"**Gender:** {patient[3]}")
            st.write(f"**Phone:** {patient[4]}")
            st.write(f"**Weight:** {patient[5]} kg")
            st.write(f"**Allergy:** {patient[6]}")
            st.write(f"**Language:** {patient[7]}")
            st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='chat-card'>", unsafe_allow_html=True)
        st.subheader("💬 Doctor Consultation")

        for m in st.session_state.chat:
            st.chat_message(m["role"]).write(m["content"])

        with st.expander("🎤 Voice / 📎 Reports", expanded=False):
            audio = st.audio_input(" ")
            st.file_uploader(" ", accept_multiple_files=True)

        if audio:
            audio_id = str(audio)
            if audio_id != st.session_state.last_audio_id:
                try:
                    text = voice_to_text(audio, st.session_state.language)
                    st.session_state.last_audio_id = audio_id
                    st.session_state.chat.append({"role": "user", "content": text})
                    reply = doctor_ai(text, patient, st.session_state.language)
                    st.session_state.chat.append({"role": "assistant", "content": reply})
                    st.rerun()
                except:
                    st.warning("Voice unclear")

        user_text = st.chat_input("Describe your problem")
        if user_text:
            st.session_state.chat.append({"role": "user", "content": user_text})
            reply = doctor_ai(user_text, patient, st.session_state.language)
            st.session_state.chat.append({"role": "assistant", "content": reply})
            st.rerun()

        # ✅ GUARANTEED PDF DOWNLOAD
        if st.session_state.final_rx:
            pdf_path = create_pdf(patient, st.session_state.final_rx)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "⬇ Download Prescription PDF",
                    data=f,
                    file_name="Prescription.pdf",
                    mime="application/pdf"
                )

        st.markdown("</div>", unsafe_allow_html=True)

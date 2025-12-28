import os
import uuid
import sqlite3
import tempfile
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

.patient-card, .chat-card, .prescription-card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}

.chat-container {
    height: 420px;
    overflow-y: auto;
    padding: 10px;
    display: flex;
    flex-direction: column;
}

.user-msg {
    background-color: #DCF8C6;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 8px;
    align-self: flex-end;
    max-width: 70%;
}

.assistant-msg {
    background-color: #EAEAEA;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 8px;
    align-self: flex-start;
    max-width: 70%;
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
</style>
""", unsafe_allow_html=True)

# ================= GROQ =================
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    st.error("GROQ_API_KEY not set")
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
st.session_state.setdefault("pid", None)
st.session_state.setdefault("language", "English")

# ================= VOICE =================
def voice_to_text(audio, lang):
    r = sr.Recognizer()
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(audio.read())
        path = f.name
    with sr.AudioFile(path) as src:
        data = r.record(src)
    try:
        return r.recognize_google(
            data,
            language={"English":"en-IN","Hindi":"hi-IN","Telugu":"te-IN"}.get(lang,"en-IN")
        )
    except:
        return None

# ================= PDF =================
def create_pdf(patient, rx):
    file = "Prescription.pdf"
    doc = SimpleDocTemplate(file, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>AI VIRTUAL DOCTOR – PRESCRIPTION</b>", styles["Title"]))
    story.append(Spacer(1,12))

    story.append(Paragraph(
        f"""
        Name: {patient[1]}<br/>
        Age/Gender: {patient[2]} / {patient[3]}<br/>
        Phone: {patient[4]}<br/>
        Weight: {patient[5]} kg<br/>
        Allergy: {patient[6]}<br/>
        Date: {datetime.now().strftime('%d-%b-%Y')}
        """, styles["Normal"]
    ))

    story.append(Spacer(1,12))
    for part in rx.split("\n\n"):
        story.append(Paragraph(part.replace("\n","<br/>"), styles["Normal"]))
        story.append(Spacer(1,10))

    doc.build(story)
    return file

# ================= AI =================
def doctor_ai(user_text, patient, lang):
    prompt = f"""
You are a professional medical doctor.
Ask only ONE question at a time.
Provide FINAL PRESCRIPTION when sufficient info is collected.

Language: {lang}
Patient: {patient[1]}, {patient[2]} years, {patient[3]}
"""
    messages = [{"role":"system","content":prompt}] + st.session_state.chat
    messages.append({"role":"user","content":user_text})

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

# ================= WELCOME =================
if st.session_state.page == "welcome":
    st.markdown("""
    <div style="padding:70px;text-align:center;">
    <h1>🩺 AI Virtual Doctor</h1>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Start Consultation"):
        st.session_state.page = "register"

# ================= REGISTER =================
elif st.session_state.page == "register":
    st.header("Patient Registration")

    name = st.text_input("Name")
    age = st.number_input("Age",1,120)
    gender = st.selectbox("Gender",["Male","Female"])
    phone = st.text_input("Phone")
    weight = st.text_input("Weight")
    allergy = st.text_input("Allergy")
    lang = st.selectbox("Language",["English","Hindi","Telugu"])

    if st.button("Proceed"):
        pid = str(uuid.uuid4())[:8]
        c.execute("INSERT INTO patients VALUES (?,?,?,?,?,?,?,?)",
                  (pid,name,age,gender,phone,weight,allergy,lang))
        conn.commit()
        st.session_state.pid = pid
        st.session_state.language = lang
        st.session_state.page = "consult"

# ================= CONSULT =================
else:
    c.execute("SELECT * FROM patients WHERE id=?", (st.session_state.pid,))
    patient = c.fetchone()

    left, right = st.columns([1.5, 3.5])

    with left:
        if st.session_state.show_patient:
            st.markdown("<div class='patient-card'>", unsafe_allow_html=True)
            st.subheader("Patient Information")
            st.write(f"Name: {patient[1]}")
            st.write(f"Age: {patient[2]}")
            st.write(f"Gender: {patient[3]}")
            st.write(f"Phone: {patient[4]}")
            st.write(f"Weight: {patient[5]}")
            st.write(f"Allergy: {patient[6]}")
            st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='chat-card'>", unsafe_allow_html=True)
        st.markdown("<h2>🩺 Doctor Consultation</h2>", unsafe_allow_html=True)

        # Chat Messages
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for m in st.session_state.chat:
            cls = "user-msg" if m["role"]=="user" else "assistant-msg"
            st.markdown(f'<div class="{cls}">{m["content"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Text Input
        user_text = st.chat_input("Type your message")
        if user_text:
            st.session_state.chat.append({"role":"user","content":user_text})
            reply = doctor_ai(user_text, patient, st.session_state.language)
            st.session_state.chat.append({"role":"assistant","content":reply})
            st.experimental_rerun()

        # Mic
        audio = st.audio_input("Click to record")
        if audio:
            text = voice_to_text(audio, st.session_state.language)
            if text:
                st.session_state.chat.append({"role":"user","content":text})
                reply = doctor_ai(text, patient, st.session_state.language)
                st.session_state.chat.append({"role":"assistant","content":reply})
                st.experimental_rerun()

        # Upload
        files = st.file_uploader(
            "Upload Reports / Images",
            accept_multiple_files=True,
            type=["png","jpg","jpeg","pdf"]
        )
        if files:
            st.session_state.uploads.extend(files)

        st.markdown("</div>", unsafe_allow_html=True)

import streamlit as st
from ai_agent import get_ai_response, generate_prescription
from pdf_utils import create_prescription_pdf

st.set_page_config(
    page_title="AI Virtual Doctor",
    page_icon="🩺",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "welcome"

if "patient" not in st.session_state:
    st.session_state.patient = {}

if "chat" not in st.session_state:
    st.session_state.chat = []

# ---------------- WELCOME PAGE ----------------
def welcome_page():
    st.markdown("""
    <div style="text-align:center; padding:40px">
        <h1 style="color:#0b5ed7;">🩺 AI Virtual Doctor</h1>
        <h3>Your Smart Healthcare Assistant</h3>
        <p>Consult an AI-powered doctor for preliminary medical guidance</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Start Registration", use_container_width=True):
        st.session_state.page = "register"
        st.rerun()

# ---------------- PATIENT REGISTRATION ----------------
def registration_page():
    st.header("🧾 Patient Registration")

    with st.form("patient_form"):
        name = st.text_input("Full Name")
        age = st.number_input("Age", min_value=1, max_value=120)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        phone = st.text_input("Phone Number")
        weight = st.number_input("Weight (kg)", min_value=1)
        allergy = st.text_input("Any Allergies?")
        submitted = st.form_submit_button("Proceed to Consultation")

    if submitted:
        st.session_state.patient = {
            "name": name,
            "age": age,
            "gender": gender,
            "phone": phone,
            "weight": weight,
            "allergy": allergy
        }
        st.session_state.page = "consult"
        st.rerun()

# ---------------- CONSULTATION PAGE ----------------
def consultation_page():
    st.subheader("💬 Doctor Consultation")

    # Sidebar Patient Info
    with st.sidebar:
        st.header("👤 Patient Info")
        for k, v in st.session_state.patient.items():
            st.write(f"**{k.capitalize()}**: {v}")

    user_input = st.text_input("Describe your symptoms")

    if st.button("🧠 Consult AI Doctor"):
        if user_input:
            response = get_ai_response(user_input, st.session_state.chat)
            st.session_state.chat.append(("Patient", user_input))
            st.session_state.chat.append(("Doctor", response))
            st.rerun()

    # Chat History
    for role, msg in st.session_state.chat:
        if role == "Patient":
            st.markdown(f"**🧑 Patient:** {msg}")
        else:
            st.markdown(f"**🩺 Doctor:** {msg}")

    if st.button("📄 Generate Prescription"):
        prescription = generate_prescription(
            st.session_state.patient,
            st.session_state.chat
        )
        pdf = create_prescription_pdf(
            st.session_state.patient,
            prescription
        )
        st.download_button(
            "⬇️ Download Prescription PDF",
            pdf,
            file_name="prescription.pdf",
            mime="application/pdf"
        )

# ---------------- ROUTER ----------------
if st.session_state.page == "welcome":
    welcome_page()
elif st.session_state.page == "register":
    registration_page()
elif st.session_state.page == "consult":
    consultation_page()

# ---------------- DISCLAIMER ----------------
st.markdown("---")
st.warning("⚠️ This AI provides general medical guidance only. Consult a certified doctor for treatment.")

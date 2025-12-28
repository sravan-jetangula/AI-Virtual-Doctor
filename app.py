import streamlit as st
from ai_agent import get_ai_response

# -------------------------------------------------
# PAGE CONFIG (must be first Streamlit command)
# -------------------------------------------------
st.set_page_config(
    page_title="AI Virtual Doctor",
    page_icon="🩺",
    layout="centered"
)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown(
    """
    <h1 style="text-align:center;">🩺 AI Virtual Doctor</h1>
    <p style="text-align:center;">
    Describe your health issue and get AI-powered medical guidance
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# SESSION STATE (same flow as PowerShell)
# -------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1

if "history" not in st.session_state:
    st.session_state.history = []

# -------------------------------------------------
# STEP 1 – SYMPTOMS INPUT
# -------------------------------------------------
if st.session_state.step == 1:
    st.subheader("🧍 Patient")
    symptom = st.text_input(
        "Describe your main symptom",
        placeholder="Example: I have fever since last night"
    )

    if st.button("Continue"):
        if symptom.strip():
            st.session_state.history.append(("Patient", symptom))
            st.session_state.step = 2
        else:
            st.warning("Please enter your symptom.")

# -------------------------------------------------
# STEP 2 – FOLLOW-UP QUESTIONS
# -------------------------------------------------
elif st.session_state.step == 2:
    st.subheader("🩺 AI Doctor")

    st.write("Thank you. I need a few more details:")

    duration = st.text_input("⏱ Since when do you have this issue?")
    severity = st.selectbox("📊 Severity", ["Mild", "Moderate", "Severe"])
    reports = st.radio("📄 Any previous medical reports?", ["No", "Yes"])

    if st.button("Analyze"):
        if duration.strip():
            combined_input = f"""
            Symptom: {st.session_state.history[0][1]}
            Duration: {duration}
            Severity: {severity}
            Reports: {reports}
            """

            response = get_ai_response(combined_input)

            st.session_state.history.append(("AI Doctor", response))
            st.session_state.step = 3
        else:
            st.warning("Please answer all questions.")

# -------------------------------------------------
# STEP 3 – RESULT (same as PowerShell output)
# -------------------------------------------------
elif st.session_state.step == 3:
    st.subheader("🧾 Medical Assessment")

    for role, text in st.session_state.history:
        if role == "Patient":
            st.markdown(f"**🧍 Patient:** {text}")
        else:
            st.markdown(f"**🩺 AI Doctor:** {text}")

    st.success("✔ Consultation completed")

    if st.button("🔄 New Consultation"):
        st.session_state.step = 1
        st.session_state.history = []

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown(
    """
    <hr>
    <small>
    ⚠️ This AI provides informational guidance only.  
    Always consult a certified doctor for medical decisions.
    </small>
    """,
    unsafe_allow_html=True
)

import streamlit as st
from ai_agent import get_ai_response
from voice import get_voice_input

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="AI Virtual Doctor",
    page_icon="🩺",
    layout="centered"
)

# -------------------------------
# Session State
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------------------
# Header
# -------------------------------
st.markdown(
    """
    <h1 style="text-align:center; color:#2E86C1;">🩺 AI Virtual Doctor</h1>
    <p style="text-align:center;">
        Describe your symptoms and receive AI-powered guidance.<br>
        <b>This tool is for educational purposes only.</b>
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Patient Input Section
# -------------------------------
st.subheader("💬 Doctor Consultation")

user_input = st.text_input(
    "Describe your symptoms:",
    placeholder="Example: I have fever and headache for 2 days"
)

# Optional (disabled) voice input
with st.expander("🎤 Voice Input (Cloud Limitation)"):
    voice_text = get_voice_input()
    if voice_text:
        user_input = voice_text

# -------------------------------
# Submit Button
# -------------------------------
if st.button("🧠 Get Medical Advice"):

    if not user_input.strip():
        st.warning("Please enter your symptoms.")
    else:
        # Save user message
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )

        # Get AI response
        with st.spinner("Analyzing your symptoms..."):
            try:
                ai_reply = get_ai_response(user_input)
            except Exception as e:
                ai_reply = "⚠️ Sorry, something went wrong while processing your request."

        # Save AI response
        st.session_state.chat_history.append(
            {"role": "assistant", "content": ai_reply}
        )

# -------------------------------
# Chat History Display
# -------------------------------
if st.session_state.chat_history:
    st.subheader("🗂 Consultation History")

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f"<div style='background:#D6EAF8; padding:10px; border-radius:10px; margin-bottom:5px;'>"
                f"<b>👤 You:</b> {msg['content']}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div style='background:#E8F8F5; padding:10px; border-radius:10px; margin-bottom:10px;'>"
                f"<b>🤖 Doctor AI:</b> {msg['content']}</div>",
                unsafe_allow_html=True
            )

# -------------------------------
# Footer
# -------------------------------
st.markdown(
    """
    <hr>
    <p style="text-align:center; font-size:13px;">
        ⚠️ This AI does not replace a licensed medical professional.<br>
        If symptoms are severe or persistent, consult a doctor immediately.
    </p>
    """,
    unsafe_allow_html=True
)

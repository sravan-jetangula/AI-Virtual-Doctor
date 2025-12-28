import streamlit as st
import os
from groq import Groq

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Virtual Doctor",
    page_icon="🩺",
    layout="centered"
)

# ---------------- API KEY ----------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)

# ---------------- SAFE AI INIT ----------------
client = None
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)

# ---------------- UI HEADER ----------------
st.markdown(
    """
    <h1 style="text-align:center;color:#2E86C1;">🩺 AI Virtual Doctor</h1>
    <p style="text-align:center;">
    Describe your health problem and get AI-powered guidance
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- INPUT ----------------
symptoms = st.text_area(
    "📝 Describe your symptoms",
    placeholder="Example: I have fever and headache since yesterday",
    height=120
)

# ---------------- BUTTON ----------------
if st.button("🧠 Consult AI Doctor"):
    if not symptoms.strip():
        st.warning("Please describe your symptoms.")
    elif not client:
        st.error("AI service is not configured. Add GROQ_API_KEY.")
    else:
        with st.spinner("AI Doctor is analyzing your symptoms..."):
            try:
                response = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an AI medical assistant. "
                                "Ask follow-up questions if needed and "
                                "give general medical guidance. "
                                "Do NOT give final diagnosis."
                            )
                        },
                        {
                            "role": "user",
                            "content": symptoms
                        }
                    ],
                    temperature=0.4
                )

                ai_reply = response.choices[0].message.content

                st.session_state.messages.append(("You", symptoms))
                st.session_state.messages.append(("AI Doctor", ai_reply))

            except Exception as e:
                st.error("Something went wrong while contacting AI.")

# ---------------- CHAT DISPLAY ----------------
st.markdown("### 💬 Doctor Consultation")

if not st.session_state.messages:
    st.info("No consultation yet. Start by describing your symptoms.")
else:
    for role, msg in st.session_state.messages:
        if role == "You":
            st.markdown(f"**🧍 You:** {msg}")
        else:
            st.markdown(f"**🩺 AI Doctor:** {msg}")

# ---------------- DISCLAIMER ----------------
st.markdown(
    """
    <hr>
    ⚠️ **Disclaimer:**  
    This AI provides general guidance only.  
    Always consult a certified doctor for medical decisions.
    """
)

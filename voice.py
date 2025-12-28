import streamlit as st

def get_voice_input():
    """
    Voice input is disabled on Streamlit Cloud because
    audio devices and PyAudio are not supported.
    """
    st.warning("🎤 Voice input is disabled on Streamlit Cloud. Please use text input.")
    return None

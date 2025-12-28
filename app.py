import os
import streamlit as st
from groq import Groq

def get_api_key():
    """
    Safely fetch Groq API key from Streamlit secrets or environment.
    """
    if "GROQ_API_KEY" in st.secrets:
        return st.secrets["GROQ_API_KEY"]
    return os.getenv("GROQ_API_KEY")


def get_ai_response(user_input: str) -> str:
    """
    Returns AI medical guidance response.
    App will NOT crash if API key is missing.
    """

    api_key = get_api_key()

    # Graceful handling (NO crash)
    if not api_key:
        return (
            "⚠️ **AI service not configured**\n\n"
            "The Groq API key is missing.\n\n"
            "If you are the developer:\n"
            "• Go to **Streamlit Cloud → Manage App → Secrets**\n"
            "• Add:\n\n"
            "```\n"
            "GROQ_API_KEY = \"your_api_key_here\"\n"
            "```\n\n"
            "The app UI is working correctly."
        )

    try:
        client = Groq(api_key=api_key)

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional AI medical assistant. "
                        "Provide safe, clear, non-diagnostic medical guidance. "
                        "Always include a medical disclaimer."
                    )
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            temperature=0.4,
            max_tokens=500
        )

        return completion.choices[0].message.content

    except Exception as e:
        return (
            "⚠️ **AI service error**\n\n"
            "The AI service is temporarily unavailable.\n\n"
            "Please try again later."
        )

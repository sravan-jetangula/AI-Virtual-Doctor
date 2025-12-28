import os
from groq import Groq

# =====================================================
# Load GROQ API key securely from environment variable
# =====================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "❌ GROQ_API_KEY not found. "
        "Please set it as an environment variable."
    )

client = Groq(api_key=GROQ_API_KEY)


def doctor_ai_response(user_input, chat_history, patient, language):
    """
    Generates AI doctor response using Groq LLM.
    """

    system_prompt = f"""
You are a professional medical doctor.

Rules:
- Ask ONLY one medical question at a time.
- Ask relevant follow-up questions based on symptoms.
- Be polite, calm, and professional.
- When enough information is collected, clearly provide:

FINAL PRESCRIPTION
- Diagnosis
- Medicines (with dosage & duration)
- Additional Instructions
- Warning signs
- Follow-up advice

Language: {language}

Patient Details:
Name: {patient[1]}
Age: {patient[2]}
Gender: {patient[3]}
Weight: {patient[5]} kg
Allergies: {patient[6]}
"""

    messages = [{"role": "system", "content": system_prompt}]

    # Add previous chat history
    for msg in chat_history:
        messages.append(msg)

    # Add current user input
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.2,
        max_tokens=700
    )

    reply = response.choices[0].message.content.strip()
    return reply

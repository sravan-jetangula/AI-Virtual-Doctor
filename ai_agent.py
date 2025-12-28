import os
from groq import Groq

def get_client():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return None
    return Groq(api_key=key)

def get_ai_response(user_input, history):
    client = get_client()
    if not client:
        return "AI service not configured. Please add API key."

    messages = [{"role": "system", "content": "You are a professional medical doctor."}]
    for role, msg in history:
        messages.append({
            "role": "user" if role == "Patient" else "assistant",
            "content": msg
        })
    messages.append({"role": "user", "content": user_input})

    res = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages
    )
    return res.choices[0].message.content

def generate_prescription(patient, chat):
    return f"""
Patient Name: {patient['name']}
Age: {patient['age']}
Gender: {patient['gender']}

Diagnosis:
Based on the symptoms, the patient may have a viral fever.

Medicines:
- Paracetamol 500mg twice daily
- Adequate rest and hydration

Advice:
- Monitor temperature
- Seek doctor if symptoms worsen
"""

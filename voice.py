
import speech_recognition as sr
import tempfile

def voice_to_text(audio):
    r = sr.Recognizer()
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(audio.read())
        name=f.name
    with sr.AudioFile(name) as source:
        data=r.record(source)
    return r.recognize_google(data)

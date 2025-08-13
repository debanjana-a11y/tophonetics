import streamlit as st
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from phonemizer import phonemize
from io import BytesIO

st.set_page_config(page_title="Speech to IPA", page_icon="🎙", layout="centered")

st.title("🎙 Speech to British IPA Converter")

# Mic recorder widget
audio = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="⏹ Stop",
    key="recorder"
)

if audio:
    st.audio(audio["bytes"], format="audio/wav")

    # Convert bytes to a file-like object
    audio_file = BytesIO(audio["bytes"])

    # Recognize speech
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            st.markdown(f"**Recognized Text:** {text}")

            # Convert to IPA (British)
            ipa = phonemize(text, language="en-gb", backend="espeak", strip=True)
            st.markdown(f"**IPA (British):** {ipa}")

        except sr.UnknownValueError:
            st.error("Sorry, I could not understand the audio.")
        except sr.RequestError:
            st.error("Speech recognition service is not available right now.")

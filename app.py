import streamlit as st
from phonemizer import phonemize
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr

st.set_page_config(page_title="British IPA Converter", page_icon="🇬🇧", layout="wide")

st.title("🎤 British English IPA Converter")
st.write("Speak or type an English sentence to get its British IPA (phonetic) transcription.")

# Microphone recorder
audio = mic_recorder(
    start_prompt="🎙️ Start Recording",
    stop_prompt="⏹️ Stop",
    just_once=False,
    use_container_width=True
)

# Recognize speech if audio exists
sentence = st.text_input("Or type your sentence here:")

if audio is not None:
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio) as source:
        audio_data = recognizer.record(source)
        try:
            sentence = recognizer.recognize_google(audio_data)
            st.write(f"**You said:** {sentence}")
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand your speech.")
        except sr.RequestError:
            st.error("Speech recognition service unavailable.")

# Convert to IPA
if st.button("Convert to IPA", use_container_width=True):
    if sentence.strip():
        ipa_sentence = phonemize(
            sentence,
            language='en-gb',
            backend='espeak',
            strip=True,
            punctuation_marks=';:,.!?¡¿—…“”'
        )
        st.success("Conversion successful!")
        st.markdown(f"**IPA (British):** `{ipa_sentence}`")
    else:
        st.warning("Please speak or type a sentence first.")

st.markdown("---")
st.caption("Now supports voice input for hands-free IPA conversion.")

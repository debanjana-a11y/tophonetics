import streamlit as st
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from phonemizer import phonemize
from pydub import AudioSegment
from io import BytesIO
import subprocess

st.title("Speech → IPA → Audio")

# Step 1: Record audio
audio_data = mic_recorder(start_prompt="🎤 Speak", stop_prompt="⏹ Stop", key="recorder")

if audio_data:
    # Convert WebM to WAV
    webm_bytes = io.BytesIO(audio_data)
    sound = AudioSegment.from_file(webm_bytes, format="webm")
    wav_bytes = io.BytesIO()
    sound.export(wav_bytes, format="wav")
    wav_bytes.seek(0)

    # Step 2: Recognize speech
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_bytes) as source:
        audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        st.write("**Recognized Text:**", text)

    # Step 3: Convert to IPA
    ipa = phonemize(text, language="en-gb", backend="espeak", strip=True)
    st.write("**IPA:**", ipa)

    # Step 4: Generate speech from IPA
    output_wav = "ipa_audio.wav"
    subprocess.run([
        "espeak",
        "--ipa",
        "-v", "en-gb",
        "-w", output_wav,
        ipa
    ])

    # Step 5: Play IPA-generated audio
    with open(output_wav, "rb") as f:
        st.audio(f.read(), format="audio/wav")

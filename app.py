import streamlit as st
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from phonemizer import phonemize
from pydub import AudioSegment
from io import BytesIO
import subprocess

st.title("Speech → IPA → Audio")

# Step 1: Record audio
audio = mic_recorder(start_prompt="🎤 Speak", stop_prompt="⏹ Stop", key="recorder")

if audio:
    st.audio(audio["bytes"], format="audio/wav")
    # Convert WebM to WAV
    webm_data = BytesIO(audio["bytes"])
    sound = AudioSegment.from_file(webm_data, format="webm")
    wav_buffer = BytesIO()
    sound.export(wav_buffer, format="wav")
    wav_buffer.seek(0)

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

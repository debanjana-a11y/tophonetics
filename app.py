import streamlit as st
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from phonemizer import phonemize
from pydub import AudioSegment
from io import BytesIO
import subprocess
from google.cloud import texttospeech

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
    with sr.AudioFile(wav_buffer) as source:
        audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        st.write("**Recognized Text:**", text)

    # Step 3: Convert to IPA
    ipa = phonemize(text, language="en-gb", backend="espeak", strip=True)
    st.write("**IPA:**", ipa)

    # Step 4: Generate speech from IPA
    # output_wav = "ipa_audio.wav"
    # subprocess.run([
    #     "espeak",
    #     "-v", "en-GB+f2",
    #     "-s", "150",
    #     "-p", "65",
    #     "-w", output_wav,
    #     text
    # ])

    # # Step 5: Play IPA-generated audio
    # with open(output_wav, "rb") as f:
    #     st.audio(f.read(), format="audio/wav")

    client = texttospeech.TextToSpeechClient()
    # Set text input
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Configure voice (British English female)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-GB",
        name="en-GB-Wavenet-C",  # You can try C, D, or F for female voices
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    # Configure audio format
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    # Generate speech
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    # Save to file
    with open("output.wav", "wb") as out:
        out.write(response.audio_content)
        print("Audio content written to file 'output.wav'")
    # Play the audio
    with open("output.wav", "rb") as f:
        st.audio(f.read(), format="audio/wav")

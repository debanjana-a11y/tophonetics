import streamlit as st
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from phonemizer import phonemize
from io import BytesIO
import subprocess
import shutil

st.title("Speech → IPA → Audio")

# Step 1: Record audio
audio = mic_recorder(start_prompt="🎤 Speak", stop_prompt="⏹ Stop", key="recorder")

if audio:
    # play the original recorded audio (browser WebM) if desired
    # st.audio(audio["bytes"], format="audio/wav")

    # Convert WebM bytes to WAV using ffmpeg (system ffmpeg or imageio-ffmpeg)
    webm_bytes = audio["bytes"]

    ffmpeg_exe = shutil.which("ffmpeg")
    if not ffmpeg_exe:
        # try imageio-ffmpeg if available (works in many cloud envs when added to requirements)
        try:
            import imageio_ffmpeg as iioff
            ffmpeg_exe = iioff.get_ffmpeg_exe()
        except Exception:
            ffmpeg_exe = None

    if not ffmpeg_exe:
        st.error("ffmpeg not found. Install system ffmpeg (apt/yum) or add imageio-ffmpeg to requirements.txt.")
    else:
        proc = subprocess.run(
            [ffmpeg_exe, "-i", "pipe:0", "-f", "wav", "-ar", "16000", "-ac", "1", "pipe:1"],
            input=webm_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if proc.returncode != 0:
            st.error("ffmpeg conversion failed: " + proc.stderr.decode(errors="ignore")[:300])
        else:
            wav_bytes = proc.stdout
            st.audio(wav_bytes, format="audio/wav")

            wav_buffer = BytesIO(wav_bytes)
            wav_buffer.seek(0)

            # Step 2: Recognize speech
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_buffer) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data)
                    st.write("**Recognized Text:**", text)
                except sr.UnknownValueError:
                    st.error("Unsupported language or unclear audio. Please try speaking clearly in English.")
                    st.stop()  # Stop further execution
                except sr.RequestError as e:
                    st.error(f"Speech recognition request failed: {e}")
                    st.stop()

            # Step 3: Convert to IPA
            ipa = phonemize(text, language="en-gb", backend="espeak", strip=True)
            st.write("**IPA:**", ipa)

            # Step 4: Generate speech
            # Prefer Coqui TTS if available, otherwise fall back to gTTS, then espeak
            tts_done = False

            import importlib, os, traceback

            # Try Coqui TTS if installed
            try:
                if importlib.util.find_spec("TTS") is not None:
                    st.info("Attempting Coqui TTS (may download model on first run)...")
                    from TTS.api import TTS
                    output_wav = "ipa_audio.wav"
                    try:
                        with st.spinner("Generating audio with Coqui TTS..."):
                            tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)
                            tts.tts_to_file(text=text, file_path=output_wav)
                        # verify file was created
                        if not os.path.exists(output_wav):
                            raise RuntimeError("Coqui TTS finished without producing output file")
                        tts_done = True
                        st.success("Generated audio using Coqui TTS")
                    except Exception as e:
                        st.error("Coqui TTS generation failed: " + str(e))
                        st.text(traceback.format_exc())
                else:
                    st.info("Coqui TTS not installed; skipping Coqui and trying other backends.")
            except Exception as e:
                st.error("Unexpected error while checking Coqui TTS: " + str(e))
                st.text(traceback.format_exc())

            if not tts_done:
                try:
                    from gtts import gTTS
                    output_wav = "ipa_audio.mp3"
                    tts = gTTS(text=text, lang='en')
                    tts.save(output_wav)
                    # convert mp3 to wav for consistent playback
                    if ffmpeg_exe:
                        proc2 = subprocess.run([ffmpeg_exe, "-i", output_wav, "-f", "wav", "-ar", "16000", "-ac", "1", "ipa_audio.wav"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        if proc2.returncode == 0:
                            output_wav = "ipa_audio.wav"
                    tts_done = True
                    st.info("Generated audio using gTTS (Google Text-to-Speech)")
                except Exception:
                    pass

            if not tts_done:
                # Try espeak if installed
                espeak_exe = shutil.which("espeak")
                if espeak_exe:
                    output_wav = "ipa_audio.wav"
                    subprocess.run([
                        espeak_exe,
                        "-v", "en-GB+f4",
                        "-s", "120",
                        "-p", "80",
                        "-w", output_wav,
                        text
                    ])
                    tts_done = True
                    st.info("Generated audio using espeak")

            if not tts_done:
                st.error("No TTS backend available. Install Coqui TTS (TTS) or add gTTS to requirements for Streamlit Cloud, or install espeak locally.")
            else:
                # Step 5: Play generated audio
                with open(output_wav, "rb") as f:
                    st.audio(f.read(), format="audio/wav")

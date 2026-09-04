import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import os
import time
from collections import deque


# ============================================================
# SETTINGS
# ============================================================

SAMPLE_RATE = 16000
BLOCK_SIZE = 512

# Adjust this if necessary
SILENCE_THRESHOLD = 350

# Silence required before stopping
SILENCE_DURATION = 1.2

# Maximum time waiting for speech
MAX_WAIT_TIME = 8

# Maximum command length
MAX_RECORDING_TIME = 30

# Keep audio from just before speech starts
PRE_BUFFER_SECONDS = 0.5


# ============================================================
# WHISPER
# ============================================================

print("🔄 Loading Whisper...")

model = whisper.load_model("base")

print("✅ Whisper ready")


# ============================================================
# RECORD
# ============================================================

def record_audio():

    print("\n🎤 Listening...")

    silence_blocks = int(
        SILENCE_DURATION * SAMPLE_RATE / BLOCK_SIZE
    )

    max_blocks = int(
        MAX_RECORDING_TIME * SAMPLE_RATE / BLOCK_SIZE
    )

    pre_buffer_blocks = int(
        PRE_BUFFER_SECONDS * SAMPLE_RATE / BLOCK_SIZE
    )

    # Keep a small amount of audio before speech starts
    pre_buffer = deque(
        maxlen=pre_buffer_blocks
    )

    audio_blocks = []

    speaking = False
    silent_count = 0

    wait_start = time.time()
    recording_start = None

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype=np.int16,
        blocksize=BLOCK_SIZE
    ) as stream:

        for _ in range(max_blocks):

            block, overflowed = stream.read(BLOCK_SIZE)

            if overflowed:
                print("⚠️ Audio overflow")

            block = block.flatten()

            # RMS is more reliable than mean absolute volume
            rms = np.sqrt(
                np.mean(
                    block.astype(np.float32) ** 2
                )
            )

            # -----------------------------------------------
            # WAITING FOR SPEECH
            # -----------------------------------------------

            if not speaking:

                pre_buffer.append(block.copy())

                if rms > SILENCE_THRESHOLD:

                    speaking = True
                    recording_start = time.time()

                    print("🗣️ Speech detected")

                    # Include audio immediately before speech
                    audio_blocks.extend(
                        list(pre_buffer)
                    )

                    pre_buffer.clear()

                else:

                    if time.time() - wait_start > MAX_WAIT_TIME:

                        print("⏱️ No speech detected")

                        return np.array([], dtype=np.int16)

            # -----------------------------------------------
            # SPEAKING
            # -----------------------------------------------

            else:

                audio_blocks.append(block.copy())

                if rms > SILENCE_THRESHOLD:

                    silent_count = 0

                else:

                    silent_count += 1

                    if silent_count >= silence_blocks:

                        print("✅ Done listening")

                        break

                # -------------------------------------------
                # MAX RECORDING TIME
                # -------------------------------------------

                if (
                    recording_start
                    and time.time() - recording_start
                    >= MAX_RECORDING_TIME
                ):

                    print("⏱️ Maximum recording time reached")

                    break

    if not audio_blocks:

        return np.array([], dtype=np.int16)

    return np.concatenate(audio_blocks)


# ============================================================
# TRANSCRIBE
# ============================================================

def transcribe_audio():

    audio = record_audio()

    if audio.size == 0:

        return ""

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as f:

            temp_path = f.name

        wav.write(
            temp_path,
            SAMPLE_RATE,
            audio
        )

        print("🧠 Whisper is transcribing...")

        result = model.transcribe(
            temp_path,
            fp16=False,
            language="en",
            temperature=0
        )

        text = result["text"].strip()

        print(f"📝 You said: {text}")

        return text

    except Exception as e:

        print(f"❌ Whisper error: {e}")

        return ""

    finally:

        if temp_path and os.path.exists(temp_path):

            try:
                os.remove(temp_path)
            except OSError:
                pass


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 45)
    print("       JARVIS MICROPHONE TEST")
    print("=" * 45)

    while True:

        try:

            text = transcribe_audio()

            if text:
                print(f"\n👤 YOU: {text}\n")

        except KeyboardInterrupt:

            print("\n👋 STT stopped")
            break
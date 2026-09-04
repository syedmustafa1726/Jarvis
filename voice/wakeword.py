import openwakeword
from openwakeword.model import Model
import sounddevice as sd
import numpy as np
import time

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280          # 80 ms at 16 kHz
WAKE_THRESHOLD = 0.5
COOLDOWN_SECONDS = 1.5

# ---------------------------------------------------------
# DOWNLOAD MODELS
# ---------------------------------------------------------

print("🔄 Loading JARVIS wake-word model...")

openwakeword.utils.download_models()

# ---------------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------------

model = Model(
    wakeword_models=["hey_jarvis"],
    vad_threshold=0.5
)

print("✅ Wake-word model loaded")


# ---------------------------------------------------------
# WAKE WORD LISTENER
# ---------------------------------------------------------

def listen_for_wakeword():
    """
    Continuously listen for 'Hey JARVIS'.

    Returns:
        True when wake word is detected.
    """

    print("\n😴 JARVIS is sleeping...")
    print("👂 Say 'Hey JARVIS' to wake me up.")

    last_detection_time = 0

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype=np.int16,
            blocksize=CHUNK_SIZE
        ) as stream:

            while True:

                # Read microphone audio
                chunk, overflowed = stream.read(CHUNK_SIZE)

                if overflowed:
                    print("⚠️ Microphone buffer overflow")

                # Convert to 1D int16 array
                chunk = chunk.flatten().astype(np.int16)

                # Run wake-word prediction
                prediction = model.predict(chunk)

                # Check predictions
                for word, score in prediction.items():

                    if score >= WAKE_THRESHOLD:

                        current_time = time.time()

                        # Prevent accidental duplicate triggers
                        if current_time - last_detection_time < COOLDOWN_SECONDS:
                            continue

                        last_detection_time = current_time

                        print(
                            f"\n⚡ Wake word detected!"
                            f" ({score:.2f})"
                        )

                        # Reset internal model state
                        model.reset()

                        return True

    except sd.PortAudioError as e:
        print(f"\n❌ Microphone error: {e}")
        raise

    except KeyboardInterrupt:
        print("\n🛑 Wake-word listener stopped.")
        raise

    except Exception as e:
        print(f"\n❌ Wake-word error: {e}")
        raise


# ---------------------------------------------------------
# STANDALONE TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 45)
    print("        JARVIS WAKE WORD TEST")
    print("=" * 45)

    try:

        while True:

            detected = listen_for_wakeword()

            if detected:
                print("🤖 JARVIS: Yes Sir!")

                time.sleep(1)

    except KeyboardInterrupt:

        print("\n👋 Wake-word test stopped.")
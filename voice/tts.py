from elevenlabs.client import ElevenLabs
import os
import tempfile
import subprocess
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Optional: put your preferred voice ID in .env
DEFAULT_VOICE_ID = os.getenv(
    "ELEVENLABS_VOICE_ID",
    "nPczCjzI2devNBz1zQrb"
)


# ============================================================
# VALIDATE API KEY
# ============================================================

if not ELEVENLABS_API_KEY:

    raise RuntimeError(
        "❌ ELEVENLABS_API_KEY not found in .env"
    )


# ============================================================
# ELEVENLABS CLIENT
# ============================================================

client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY
)


# ============================================================
# SPEAK
# ============================================================

def speak(
    text: str,
    voice_id: str = DEFAULT_VOICE_ID
):
    """
    Convert text to speech using ElevenLabs
    and play it through FFplay.
    """

    if not text or not text.strip():
        print("⚠️ Nothing to speak.")
        return False

    temp_path = None

    try:

        print("🔊 JARVIS speaking...")

        # ----------------------------------------------------
        # Generate audio
        # ----------------------------------------------------

        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_turbo_v2",
        )

        # ----------------------------------------------------
        # Save temporary MP3
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False
        ) as f:

            temp_path = f.name

            for chunk in audio:

                if chunk:
                    f.write(chunk)

        # ----------------------------------------------------
        # Play audio
        # ----------------------------------------------------

        result = subprocess.run(
            [
                "ffplay",
                "-nodisp",
                "-autoexit",
                "-loglevel",
                "error",
                temp_path
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True
        )

        # ----------------------------------------------------
        # Check FFplay
        # ----------------------------------------------------

        if result.returncode != 0:

            print(
                f"❌ FFplay error: {result.stderr.strip()}"
            )

            return False

        return True

    except Exception as e:

        print(
            f"❌ TTS error: "
            f"{type(e).__name__}: {e}"
        )

        return False

    finally:

        # ----------------------------------------------------
        # Always delete temporary audio
        # ----------------------------------------------------

        if temp_path and os.path.exists(temp_path):

            try:
                os.remove(temp_path)

            except OSError:
                pass


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 45)
    print("        JARVIS TTS TEST")
    print("=" * 45)

    speak(
        "Hello Sir. JARVIS systems are online."
    )
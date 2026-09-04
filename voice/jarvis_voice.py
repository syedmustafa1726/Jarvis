import requests
from stt import transcribe_audio
from tts import speak
from wakeword import listen_for_wakeword

API_URL = "http://localhost:8000"
USER_NAME = "Mustafa"


def send_to_jarvis(user_input):
    """Send user's command to the JARVIS backend."""

    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "message": user_input,
                "user_name": USER_NAME
            },
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "response",
            "I'm sorry Sir, I couldn't generate a response."
        )

    except requests.exceptions.ConnectionError:
        return "Sir, I cannot connect to my backend."

    except requests.exceptions.Timeout:
        return "Sorry Sir, the request took too long."

    except Exception as e:
        print(f"❌ Backend error: {e}")
        return "I'm sorry Sir, something went wrong."


def active_conversation():
    """
    JARVIS stays awake and continues listening
    until the user tells him to sleep.
    """

    print("\n🟢 JARVIS ACTIVE")
    print("💬 You can speak normally now.")
    print("😴 Say 'go to sleep' when you're finished.\n")

    speak("I'm listening, Sir.")

    while True:

        try:

            # -----------------------------------------------
            # Listen for next command
            # -----------------------------------------------

            print("🎤 Listening...")

            user_input = transcribe_audio()

            if not user_input:
                print("⚠️ Nothing heard.")
                continue

            user_input = user_input.strip()

            print(f"\n👤 You: {user_input}")

            # -----------------------------------------------
            # Sleep commands
            # -----------------------------------------------

            sleep_words = [
                "sign off",
                "go sleep",
                "sleep",
                "stand by",
                "standby",
                "stop listening",
                "goodbye",
                "good bye",
                "exit",
                "go offline",
                "shut down",
                "quit"
            ]

            if any(
                phrase in user_input.lower()
                for phrase in sleep_words
            ):

                speak("Of course, Sir. Going to sleep.")

                print("\n😴 JARVIS sleeping...")
                return

            # -----------------------------------------------
            # Send to backend
            # -----------------------------------------------

            print("🧠 Thinking...")

            jarvis_reply = send_to_jarvis(user_input)

            # -----------------------------------------------
            # Display response
            # -----------------------------------------------

            print(f"\n🤖 JARVIS: {jarvis_reply}")

            # -----------------------------------------------
            # Speak response
            # -----------------------------------------------

            speak(jarvis_reply)

        except KeyboardInterrupt:
            raise

        except Exception as e:
            print(f"❌ Conversation error: {e}")
            continue


def voice_chat():

    print("\n🤖 JARVIS System Active")
    print("=" * 45)
    print("😴 JARVIS starts in sleep mode")
    print("🗣️ Say 'Hey JARVIS' to activate")
    print("💬 Then speak normally")
    print("😴 Say 'go to sleep' to deactivate")
    print("=" * 45)

    while True:

        try:

            # =================================================
            # SLEEP MODE
            # =================================================

            print("\n😴 JARVIS is sleeping...")
            print("👂 Waiting for 'Hey JARVIS'...")

            listen_for_wakeword()

            # =================================================
            # WAKE UP
            # =================================================

            print("\n⚡ JARVIS awakened!")

            speak(
                "Yes Sir, how can I help you?"
            )

            # =================================================
            # ACTIVE CONVERSATION
            # =================================================

            active_conversation()

        except KeyboardInterrupt:

            print("\n🛑 Shutdown requested.")

            speak("Goodbye Sir.")

            print("👋 JARVIS offline")

            break

        except Exception as e:

            print(f"\n❌ System error: {e}")

            print("🔄 Returning to sleep mode...")


if __name__ == "__main__":
    voice_chat()
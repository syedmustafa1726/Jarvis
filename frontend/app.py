import streamlit as st
import requests
import html

# ============================================================
# JARVIS CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="JARVIS",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# LIVE RENDER BACKEND
API_URL = "https://jarvis-z2ec.onrender.com"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&family=Rajdhani:wght@300;400;500;600&display=swap');

/* ---------- GLOBAL ---------- */

html, body, [class*="css"] {
    background-color: #0a0e1a;
    color: #c8d8f0;
    font-family: 'Rajdhani', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 50% 0%, #101f3a 0%, #0a0e1a 45%, #050810 100%);
}

/* ---------- TITLE ---------- */

.jarvis-title {
    font-family: 'Orbitron', monospace;
    font-size: 3rem;
    font-weight: 700;
    color: #4fc3f7;
    letter-spacing: 0.3em;
    text-shadow:
        0 0 10px rgba(79,195,247,0.5),
        0 0 30px rgba(79,195,247,0.3);
    text-align: center;
    margin-bottom: 0;
}

.jarvis-subtitle {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.85rem;
    color: #607d8b;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    text-align: center;
    margin-top: 0;
}

/* ---------- ONLINE STATUS ---------- */

.status-container {
    text-align: center;
    margin: 10px 0 20px 0;
}

.status-online {
    display: inline-block;
    padding: 5px 15px;
    border: 1px solid #4fc3f7;
    border-radius: 20px;
    color: #4fc3f7;
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    box-shadow: 0 0 15px rgba(79,195,247,0.15);
}

/* ---------- CHAT ---------- */

.chat-bubble-user {
    background: #172542;
    border: 1px solid #1e3a5f;
    border-radius: 14px 14px 3px 14px;
    padding: 0.9rem 1.1rem;
    margin: 0.7rem 0 0.7rem 3rem;
    color: #d7e7f7;
    box-shadow: 0 5px 20px rgba(0,0,0,0.15);
}

.chat-bubble-jarvis {
    background: #0d1f3c;
    border: 1px solid #4fc3f7;
    border-radius: 14px 14px 14px 3px;
    padding: 0.9rem 1.1rem;
    margin: 0.7rem 3rem 0.7rem 0;
    color: #e0f4ff;
    box-shadow:
        0 0 15px rgba(79,195,247,0.08),
        0 5px 20px rgba(0,0,0,0.15);
}

.role-label {
    font-family: 'Orbitron', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.15em;
    margin-bottom: 0.35rem;
    color: #4fc3f7;
    opacity: 0.8;
}

/* ---------- INPUT ---------- */

.stTextInput > div > div > input {
    background-color: #0d1f3c !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
    color: #c8d8f0 !important;
    font-family: 'Rajdhani', sans-serif !important;
}

.stTextInput > div > div > input:focus {
    border: 1px solid #4fc3f7 !important;
    box-shadow: 0 0 10px rgba(79,195,247,0.15) !important;
}

/* ---------- BUTTON ---------- */

.stButton > button {
    background: linear-gradient(
        135deg,
        #1565c0,
        #0d47a1
    ) !important;

    color: #4fc3f7 !important;

    border: 1px solid #4fc3f7 !important;

    border-radius: 8px !important;

    font-family: 'Orbitron', monospace !important;

    font-size: 0.7rem !important;

    letter-spacing: 0.1em !important;

    transition: all 0.2s ease-in-out;
}

.stButton > button:hover {
    box-shadow: 0 0 15px rgba(79,195,247,0.3);
    transform: translateY(-1px);
}

/* ---------- DIVIDER ---------- */

hr {
    border-color: #1e3a5f !important;
}

/* ---------- MOBILE ---------- */

@media (max-width: 600px) {

    .jarvis-title {
        font-size: 2.1rem;
        letter-spacing: 0.2em;
    }

    .chat-bubble-user {
        margin-left: 1rem;
    }

    .chat-bubble-jarvis {
        margin-right: 1rem;
    }
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_name" not in st.session_state:
    st.session_state.user_name = "Sir"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("### ⚙️ Settings")

    st.session_state.user_name = st.text_input(
        "Your name",
        value=st.session_state.user_name
    )

    st.markdown("---")

    if st.button("🔄 Reset Conversation"):

        try:

            response = requests.post(
                f"{API_URL}/reset",
                timeout=20
            )

            if response.status_code == 200:

                st.session_state.messages = []

                st.success("Conversation reset.")

                st.rerun()

            else:

                st.error("Could not reset conversation.")

        except requests.exceptions.RequestException:

            st.error("Could not connect to JARVIS backend.")

    st.markdown("---")

    st.markdown("**Model:** Groq / LLaMA")
    st.markdown("**Backend:** Render")
    st.markdown("**Connection:** HTTPS")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<p class="jarvis-title">JARVIS</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="jarvis-subtitle">'
    'Just A Rather Very Intelligent System'
    '</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="status-container">'
    '<span class="status-online">● SYSTEM ONLINE</span>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")


# ============================================================
# CHAT HISTORY
# ============================================================

for msg in st.session_state.messages:

    safe_content = html.escape(str(msg["content"]))

    if msg["role"] == "user":

        st.markdown(
            f"""
            <div class="chat-bubble-user">
                <div class="role-label">YOU</div>
                {safe_content}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class="chat-bubble-jarvis">
                <div class="role-label">JARVIS</div>
                {safe_content}
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# MESSAGE INPUT
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])

with col1:

    user_input = st.text_input(
        "Message",
        placeholder="Good evening, JARVIS...",
        label_visibility="collapsed",
        key="user_input"
    )

with col2:

    send = st.button("SEND")


# ============================================================
# SEND MESSAGE
# ============================================================

if send and user_input.strip():

    message = user_input.strip()

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": message
    })

    with st.spinner("JARVIS is thinking..."):

        try:

            response = requests.post(
                f"{API_URL}/chat",

                json={
                    "message": message,
                    "user_name": st.session_state.user_name
                },

                timeout=90
            )

            # --------------------------------------------
            # SUCCESS
            # --------------------------------------------

            if response.status_code == 200:

                data = response.json()

                jarvis_reply = data.get(
                    "response",
                    "I received your request, Sir, but no response was returned."
                )

            # --------------------------------------------
            # BACKEND ERROR
            # --------------------------------------------

            else:

                try:
                    error_data = response.json()

                    jarvis_reply = (
                        f"Backend error ({response.status_code}), Sir."
                    )

                except Exception:

                    jarvis_reply = (
                        f"Backend returned status "
                        f"{response.status_code}, Sir."
                    )

        # --------------------------------------------
        # CONNECTION ERROR
        # --------------------------------------------

        except requests.exceptions.ConnectionError:

            jarvis_reply = (
                "⚠️ I cannot reach the JARVIS backend at the moment, Sir."
            )

        # --------------------------------------------
        # TIMEOUT
        # --------------------------------------------

        except requests.exceptions.Timeout:

            jarvis_reply = (
                "⚠️ The JARVIS backend took too long to respond, Sir."
            )

        # --------------------------------------------
        # OTHER ERROR
        # --------------------------------------------

        except requests.exceptions.RequestException as e:

            jarvis_reply = (
                "⚠️ An unexpected connection error occurred, Sir."
            )

        except Exception:

            jarvis_reply = (
                "⚠️ Something went wrong while processing your request, Sir."
            )

    # Add JARVIS response
    st.session_state.messages.append({
        "role": "jarvis",
        "content": jarvis_reply
    })

    # Refresh UI
    st.rerun()
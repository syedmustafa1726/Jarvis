import streamlit as st
import requests

st.set_page_config(
    page_title="JARVIS",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;400;500&display=swap');

  html, body, [class*="css"] {
    background-color: #0a0e1a;
    color: #c8d8f0;
    font-family: 'Rajdhani', sans-serif;
  }
  .jarvis-title {
    font-family: 'Orbitron', monospace;
    font-size: 3rem;
    font-weight: 700;
    color: #4fc3f7;
    letter-spacing: 0.3em;
    text-shadow: 0 0 30px rgba(79,195,247,0.5);
    text-align: center;
  }
  .jarvis-subtitle {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.85rem;
    color: #546e7a;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    text-align: center;
  }
  .chat-bubble-user {
    background: #1a2744;
    border: 1px solid #1e3a5f;
    border-radius: 12px 12px 2px 12px;
    padding: 0.8rem 1.1rem;
    margin: 0.5rem 0 0.5rem 3rem;
    color: #c8d8f0;
  }
  .chat-bubble-jarvis {
    background: #0d1f3c;
    border: 1px solid #4fc3f7;
    border-radius: 12px 12px 12px 2px;
    padding: 0.8rem 1.1rem;
    margin: 0.5rem 3rem 0.5rem 0;
    color: #e0f4ff;
    box-shadow: 0 0 12px rgba(79,195,247,0.08);
  }
  .role-label {
    font-family: 'Orbitron', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.15em;
    margin-bottom: 0.3rem;
    opacity: 0.6;
  }
  .stTextInput > div > div > input {
    background-color: #0d1f3c !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
    color: #c8d8f0 !important;
  }
  .stButton > button {
    background: linear-gradient(135deg, #1565c0, #0d47a1) !important;
    color: #4fc3f7 !important;
    border: 1px solid #4fc3f7 !important;
    border-radius: 8px !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
  }
</style>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_name" not in st.session_state:
    st.session_state.user_name = "Sir"

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.session_state.user_name = st.text_input("Your name", value=st.session_state.user_name)
    st.markdown("---")
    if st.button("🔄 Reset Conversation"):
        try:
            requests.post(f"{API_URL}/reset")
            st.session_state.messages = []
            st.rerun()
        except:
            st.error("Could not connect to JARVIS backend.")
    st.markdown("---")
    st.markdown("**Model:** LLaMA 3.2 (local)")
    st.markdown("**Privacy:** 100% local")
    st.markdown("**Cost:** $0")

st.markdown('<p class="jarvis-title">JARVIS</p>', unsafe_allow_html=True)
st.markdown('<p class="jarvis-subtitle">Just A Rather Very Intelligent System — Online</p>', unsafe_allow_html=True)
st.markdown("---")

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="chat-bubble-user">
          <div class="role-label">YOU</div>
          {msg["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-bubble-jarvis">
          <div class="role-label">JARVIS</div>
          {msg["content"]}
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        "Message",
        placeholder="Good morning, JARVIS...",
        label_visibility="collapsed",
        key="user_input"
    )

with col2:
    send = st.button("SEND")

if send and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("JARVIS is thinking..."):
        try:
            res = requests.post(
                f"{API_URL}/chat",
                json={"message": user_input, "user_name": st.session_state.user_name},
                timeout=60
            )
            if res.status_code == 200:
                jarvis_reply = res.json()["response"]
            else:
                jarvis_reply = "I encountered an error, Sir. Please check the backend."
        except requests.exceptions.ConnectionError:
            jarvis_reply = "⚠️ Cannot connect to JARVIS backend. Make sure it's running on port 8000."

    st.session_state.messages.append({"role": "jarvis", "content": jarvis_reply})
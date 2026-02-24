# ...existing code...
import streamlit as st
import os
import dotenv
from datetime import datetime
import json

# try to import the Gemini adapter; fall back to demo if not installed
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    HAS_GENAI = True
except Exception:
    HAS_GENAI = False

dotenv.load_dotenv()

# --- App header (Streamlit-only UI) ---
st.set_page_config(page_title="Gemini Chat — Samprit", page_icon="🤖", layout="wide")
st.title("🤖 Gemini Chat")
st.subheader("A friendly chatbot ")

# --- Sidebar: settings and API key (session only) ---
with st.sidebar:
    st.header("⚙️ Settings")
    model = st.selectbox("Model", ["gemini-2.5-flash"], index=0)
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.01)
    max_tokens = st.slider("Max output tokens", 50, 1024, 256, 10)
    st.markdown("---")

    st.header("🔐 API Key (session)")
    env_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if env_key:
        st.info("API key loaded from environment.")
        if st.button("Clear session key"):
            os.environ.pop("GEMINI_API_KEY", None)
            os.environ.pop("GOOGLE_API_KEY", None)
            st.experimental_rerun()
    else:
        with st.form("key_form"):
            entered = st.text_input("Paste GEMINI_API_KEY (won't be saved)", type="password")
            use = st.form_submit_button("Use key for session")
            if use and entered:
                os.environ["GEMINI_API_KEY"] = entered
                os.environ["GOOGLE_API_KEY"] = entered
                st.success("API key set for this session")
                st.experimental_rerun()

    st.markdown("---")
    st.header("📁 Files")
    uploaded = st.file_uploader("Upload file (optional)", type=["txt", "md", "pdf"])
    if uploaded:
        st.success(f"Uploaded: {uploaded.name}")

    st.markdown("---")
    st.header("💾 Export")
    if st.button("Export chat history (JSON)"):
        if "history" in st.session_state and st.session_state.history:
            payload = json.dumps(st.session_state.history, ensure_ascii=False, indent=2)
            st.download_button("Download JSON", payload, file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
        else:
            st.info("No chat history to export")

    st.markdown("---")
    st.caption("© Copyright by Samprit")

# --- Initialize session state ---
if "history" not in st.session_state:
    st.session_state.history = []  # list of {"role": "user"/"assistant", "text": "...", "time": "..."}
if "last_model" not in st.session_state:
    st.session_state.last_model = model

# --- Initialize LLM if possible ---
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
llm = None
if HAS_GENAI and api_key:
    try:
        os.environ["GOOGLE_API_KEY"] = api_key
        llm = ChatGoogleGenerativeAI(model=model)
    except Exception as e:
        st.warning("Failed to initialize Gemini client; running in demo mode.")
        llm = None
elif not HAS_GENAI:
    st.info("langchain_google_genai not installed — running demo mode.")

# --- Helper functions ---
def add_message(role, text):
    st.session_state.history.append({"role": role, "text": text, "time": datetime.now().isoformat()})

def clear_history():
    st.session_state.history = []

def generate_reply(prompt):
    if llm:
        try:
            resp = llm.invoke(prompt, temperature=temperature, max_output_tokens=max_tokens)
            # resp may be object; try to extract textual content
            content = getattr(resp, "content", None) or str(resp)
            return content
        except Exception as e:
            return f"Error from model: {e}"
    # Demo fallback reply
    return f"Demo reply: I received your prompt: {prompt[:300]}"

# --- Top bar with actions ---
cols = st.columns([1,1,1,1])
with cols[0]:
    st.metric("Messages", len(st.session_state.history))
with cols[1]:
    st.metric("Model", model)
with cols[2]:
    if st.button("Clear chat"):
        clear_history()
        st.experimental_rerun()
with cols[3]:
    if st.button("Refresh"):
        st.experimental_rerun()

# --- Main chat area (left) and info (right) ---
left, right = st.columns([3,1])

with left:
    st.header("💬 Chat")
    # Render history using chat_message component
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.chat_message("user", avatar="🧑‍💻").write(msg["text"])
        else:
            st.chat_message("assistant", avatar="🤖").write(msg["text"])

    # Use st.chat_input so behaviour feels native
    user_text = st.chat_input("Type your message and press Enter...")
    if user_text:
        add_message("user", user_text)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                reply = generate_reply(user_text)
                add_message("assistant", reply)
                st.write(reply)

with right:
    st.header("ℹ️ Info & Tips")
    st.markdown("- Be specific with prompts.")
    st.markdown("- Use the sidebar to set temperature and tokens.")
    st.markdown("- Upload a file to reference (demo only).")
    st.divider()
    st.subheader("Last activity")
    if st.session_state.history:
        last = st.session_state.history[-1]
        st.write(f"{last['role'].title()} at {last['time']}")
    else:
        st.write("No messages yet.")
    st.divider()
    st.subheader("Session")
    st.write("API key set:" , bool(api_key))
    st.write("Adapter installed:", HAS_GENAI)

# --- File preview (if uploaded) ---
if uploaded:
    st.header("📄 Uploaded file preview")
    if uploaded.type.startswith("text"):
        text = uploaded.getvalue().decode(errors="ignore")
        st.text_area(uploaded.name, text, height=300)
    else:
        st.write("Binary file preview not shown in demo.")

# --- Footer ---
st.write("---")
st.caption("Built with Streamlit • Keep your API key secret")
st.markdown("**© 2024 Samprit — All rights reserved**") 
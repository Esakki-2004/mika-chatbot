import streamlit as st
from google import genai
from google.genai import types

# --- Page Configuration ---
st.set_page_config(
    page_title="Mika AI Chat",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- ADVANCED CUSTOM CSS (DARK THEME) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp { background-color: #0E1117; color: #FAFAFA; }

    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #333; }
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label { color: #E0E0E0 !important; }

    /* Chat Bubbles */
    .stChatMessage { background-color: #1E1E1E; border: 1px solid #333; border-radius: 12px; padding: 15px; margin-bottom: 10px; }
    
    /* User Bubble - Blue Theme for Gemini */
    [data-testid="stChatMessageContentUser"] {
        background: linear-gradient(135deg, #4285F4 0%, #4FC3F7 100%);
        color: white;
        border-radius: 15px;
        padding: 10px 15px;
    }

    /* Input Box */
    .stChatInput { background-color: #1E1E1E; border: 1px solid #333; border-radius: 12px; }
    .stChatInput textarea { color: #FFFFFF !important; }
    
    /* Buttons */
    .stButton button { background-color: #333; color: white; border: 1px solid #555; }
    .stButton button:hover { background-color: #444; border-color: #4285F4; }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0E1117; }
    ::-webkit-scrollbar-thumb { background: #555; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Configuration ---
with st.sidebar:
    st.markdown("<h2 style='color: #4285F4; font-weight: bold;'>🤖 Mika AI</h2>", unsafe_allow_html=True)
    
    # API Key Input (Secure)
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("API Key Loaded ✅")
    else:
        api_key = st.text_input("Google API Key:", type="password", key="gemini_key_input")
    
    st.divider()
    
    # System Prompt
    system_instruction = st.text_area(
        "System Instructions", 
        value="You are Mika, a clever Python-built assistant.", 
        height=100
    )
    
    # Model Selection
    model_choice = st.selectbox("Model", ["gemini-2.0-flash", "gemini-1.5-pro"])
    
    # Clear History Button
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.rerun()

# --- Session State Initialization ---
# We use Session State instead of JSON files for web apps
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

# --- Main Chat Logic ---

# 1. Check for API Key
if not api_key:
    st.info("👈 Please enter your Google API Key in the sidebar to start.")
    st.stop()

# 2. Initialize Client and Chat Session
try:
    # Initialize the Google Gen AI Client
    client = genai.Client(api_key=api_key)
    
    # Create a new chat session if one doesn't exist
    if st.session_state.chat_session is None:
        st.session_state.chat_session = client.chats.create(
            model=model_choice,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        
        # Add initial greeting to UI history only
        if not st.session_state.messages:
            greeting = "Hi! I'm Mika. How can I help you today?"
            st.session_state.messages.append({"role": "assistant", "content": greeting})
            
except Exception as e:
    st.error(f"Error initializing client: {e}")
    st.stop()

# 3. Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. Handle User Input
if prompt := st.chat_input("Talk to Mika..."):
    # Display user message immediately
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Send to API and get response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Send message to the existing chat session (SDK handles history)
            response = st.session_state.chat_session.send_message(prompt)
            full_response = response.text
            
            # Optional: Typing effect
            import time
            for i in range(len(full_response)):
                time.sleep(0.005)
                response_placeholder.markdown(full_response[:i+1] + "▌")
            
            response_placeholder.markdown(full_response)
            
            # Save to UI history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"AI Error: {e}")

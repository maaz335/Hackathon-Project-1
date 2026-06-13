import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="SupportBot | Hackathon 2026", page_icon="🤖", layout="centered")

st.title("🤖 SupportBot Assistant")
st.markdown("Your 24/7 AI-powered guide. Ask me anything and I will answer contextually, just like ChatGPT!")

# Custom CSS for a clean look
st.markdown("""
<style>
    [data-testid="stChatMessageContent"] {
        padding: 1.5rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🛠️ Configuration")
    st.markdown("To make this chatbot 100% Free and incredibly smart, we are using the Google Gemini Engine with an auto-switching multi-key system.")
    
    st.divider()
    st.markdown("### 🧠 About SupportBot")
    st.markdown("""
    This bot uses **Generative AI (LLMs)** to understand the context of your questions and maintain conversational memory.
    
    *Engine: Google Gemini 1.5 Flash*  
    *Status: Online 🟢*
    """)
    st.caption("Developed for Hackathon 2026. Version 2.0 (GenAI Edition)")

# Fetch API Keys from Streamlit Secrets securely
USER_KEYS = []
if "GEMINI_KEYS" in st.secrets:
    USER_KEYS = st.secrets["GEMINI_KEYS"]
else:
    st.error("API Keys not found in Secrets! If deploying, add them to Streamlit Cloud Secrets.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I am the SupportBot (powered by Gemini). How can I help you today?"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is your question?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    keys_to_try = []
    keys_to_try.extend(USER_KEYS)

    success = False
    error_msg = ""

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            for key in keys_to_try:
                try:
                    # Configure Gemini API
                    genai.configure(api_key=key.strip())
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    # Convert session state messages to Gemini format
                    gemini_history = []
                    for msg in st.session_state.messages[:-1]:
                        role = "user" if msg["role"] == "user" else "model"
                        gemini_history.append({"role": role, "parts": [msg["content"]]})
                        
                    # Start chat session with history
                    chat = model.start_chat(history=gemini_history)
                    response = chat.send_message(prompt)
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    success = True
                    break # Success! Break out of the fallback loop
                except Exception as e:
                    error_msg = str(e)
                    continue # Failed (e.g. rate limit), try the next key
            
            if not success:
                st.error(f"❌ Error: All fallback keys failed or got exhausted! Please generate a new key and paste it in the sidebar. Last Error: {error_msg}")

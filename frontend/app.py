"""
app.py — Industry-Standard Streamlit Chat UI for College Admission Chatbot

Run:  streamlit run frontend/app.py
"""

import sys
import os
import time
import requests
import streamlit as st
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="College Admission Assistant | AdmissionBot AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "College Admission Chatbot powered by RAG technology"}
)

# ── Professional CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main {
        background: #ffffff;
    }
    
    /* Header Styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 0;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    
    .header-content {
        color: white;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin: 0;
    }
    
    .header-subtitle {
        font-size: 0.95rem;
        opacity: 0.95;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    /* Chat Container */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Message Styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
        word-wrap: break-word;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-left: auto;
        max-width: 80%;
    }
    
    .assistant-message {
        background: #f8f9fa;
        color: #2d3748;
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        word-wrap: break-word;
        font-size: 0.95rem;
        line-height: 1.6;
        max-width: 100%;
    }
    
    /* Source Badge */
    .source-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #f0f2f5 100%);
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    .source-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 0.75rem;
        margin: 4px 4px 4px 0;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
    }
    
    .relevance-bar {
        height: 6px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 3px;
        margin-top: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.7rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Input Box */
    .stChatInputContainer {
        padding: 1.5rem 0;
        background: white;
        border-top: 1px solid #e2e8f0;
    }
    
    .stChatInput input {
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stChatInput input:focus {
        border: 2px solid #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #f8f9fa !important;
        border-radius: 8px !important;
    }
    
    /* Stats Badge */
    .stats-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    /* Footer */
    .footer-container {
        text-align: center;
        padding: 2rem 1rem;
        border-top: 1px solid #e2e8f0;
        color: #718096;
        font-size: 0.85rem;
        margin-top: 3rem;
    }
    
    /* Welcome Section */
    .welcome-section {
        text-align: center;
        padding: 3rem 1rem;
        color: #718096;
    }
    
    .welcome-section h3 {
        font-size: 1.8rem;
        margin-bottom: 1rem;
        color: #2d3748;
    }
    
    .welcome-section p {
        font-size: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
API_URL = os.getenv("API_URL", "http://localhost:8000")
USE_DIRECT = True

SUGGESTED_QUESTIONS = [
    "📅 What is the last date to apply?",
    "💰 What is the B.Tech fee per year?",
    "✅ What are the eligibility criteria for MBA?",
    "📋 What documents are required for admission?",
    "🏠 Tell me about hostel facilities",
    "💼 What is the average placement package for CSE?",
]

# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None
if "response_time" not in st.session_state:
    st.session_state.response_time = 0

# ── Helper: Get Answer ────────────────────────────────────────────────────────
@st.cache_resource
def load_pipeline():
    """Load the RAG pipeline once on startup"""
    try:
        from backend.rag_pipeline import answer
        return answer
    except Exception as e:
        return None

def get_answer(question: str) -> dict:
    """Get answer from pipeline or API"""
    start_time = time.time()
    
    if USE_DIRECT:
        try:
            answer_fn = load_pipeline()
            if answer_fn is None:
                return {
                    "answer": "⚠️ Could not load pipeline. Run `python backend/ingest.py` first.",
                    "sources": [],
                    "mode": "error"
                }
            result = answer_fn(question)
            st.session_state.response_time = time.time() - start_time
            return result
        except Exception as e:
            return {
                "answer": f"⚠️ Error: {str(e)}",
                "sources": [],
                "mode": "error"
            }
    else:
        try:
            resp = requests.post(f"{API_URL}/ask", json={"question": question}, timeout=15)
            resp.raise_for_status()
            st.session_state.response_time = time.time() - start_time
            return resp.json()
        except Exception as e:
            return {"answer": f"⚠️ API Error: {str(e)}", "sources": [], "mode": "error"}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🎓 **AdmissionBot AI**")
    st.markdown("*Intelligent College Admission Assistant*")
    st.markdown("---")
    
    st.markdown("#### 💡 **Quick Questions**")
    for q in SUGGESTED_QUESTIONS:
        if st.button(q, key=f"btn_{q}", use_container_width=True):
            st.session_state.pending_question = q
            st.rerun()
    
    st.markdown("---")
    st.markdown("#### ⚙️ **Settings**")
    
    col1, col2 = st.columns(2)
    with col1:
        show_sources = st.toggle("Sources", value=True, key="toggle_sources")
    with col2:
        show_mode = st.toggle("Mode", value=False, key="toggle_mode")
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.response_time = 0
        st.rerun()
    
    st.markdown("---")
    st.markdown("#### ℹ️ **About**")
    st.markdown(
        "This chatbot uses **Retrieval-Augmented Generation (RAG)** to provide "
        "accurate college admission information powered by sentence-transformers "
        "and ChromaDB vector database."
    )
    
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #718096; font-size: 0.8rem;'>"
        "<p>Built with ❤️ by Rahul Ramavath</p>"
        "<p>RAG Pipeline Project</p>"
        "</div>",
        unsafe_allow_html=True
    )

# ── Main Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-container">
    <div class="header-content">
        <div>
            <h1 class="header-title">🎓 College Admission Assistant</h1>
            <p class="header-subtitle">
                Get instant answers to all your college admission questions
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Chat Container ───────────────────────────────────────────────────────────
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="welcome-section">
        <h3>👋 Welcome to AdmissionBot</h3>
        <p>Select a quick question from the sidebar or ask your own question below</p>
        <p style='font-size: 0.9rem; margin-top: 1rem;'>
            💡 Tip: Ask about admissions, fees, eligibility, courses, hostels, or placements
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="user-message">👤 {msg["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="assistant-message">{msg["content"]}</div>',
                unsafe_allow_html=True
            )
            if msg.get("sources") and show_sources:
                with st.expander("📚 Retrieved Sources", expanded=False):
                    for src in msg["sources"]:
                        rel = src.get("relevance", 0)
                        st.markdown(
                            f'<span class="source-badge">📄 {src["source"]}</span> '
                            f'<span class="stats-badge">{rel:.0%} Relevant</span>',
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f'<div class="relevance-bar" style="width:{rel*100:.0f}%"></div>',
                            unsafe_allow_html=True
                        )
            if msg.get("mode") and show_mode:
                st.caption(f"🔍 Retrieval Mode: `{msg['mode']}`")
            if msg.get("response_time"):
                st.caption(f"⏱️ Response Time: {msg['response_time']:.2f}s")

st.markdown("</div>", unsafe_allow_html=True)

# ── Chat Input ────────────────────────────────────────────────────────────────
user_input = st.chat_input(
    "💬 Ask about admissions, fees, eligibility, courses, hostel, placements...",
    key="chat_input"
)

# Use quick-question button if clicked
question = user_input or st.session_state.pending_question
if st.session_state.pending_question:
    st.session_state.pending_question = None

if question:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })
    
    # Display user message
    st.markdown(
        f'<div class="user-message">👤 {question}</div>',
        unsafe_allow_html=True
    )
    
    # Get assistant response with loading state
    with st.spinner("🔍 Searching knowledge base..."):
        result = get_answer(question)
    
    answer_text = result.get("answer", "Sorry, I couldn't find an answer.")
    sources = result.get("sources", [])
    mode = result.get("mode", "")
    response_time = st.session_state.response_time
    
    # Add to chat history
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer_text,
        "sources": sources,
        "mode": mode,
        "response_time": response_time
    })
    
    # Display assistant response with typewriter effect
    st.markdown(f'<div class="assistant-message">', unsafe_allow_html=True)
    
    placeholder = st.empty()
    displayed = ""
    for char in answer_text:
        displayed += char
        placeholder.markdown(displayed + "▌")
        time.sleep(0.005)
    placeholder.markdown(displayed)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display sources
    if sources and show_sources:
        with st.expander("📚 Retrieved Sources", expanded=False):
            for src in sources:
                rel = src.get("relevance", 0)
                st.markdown(
                    f'<span class="source-badge">📄 {src["source"]}</span> '
                    f'<span class="stats-badge">{rel:.0%} Relevant</span>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    f'<div class="relevance-bar" style="width:{rel*100:.0f}%"></div>',
                    unsafe_allow_html=True
                )
    
    # Display retrieval mode
    if mode and show_mode:
        st.caption(f"🔍 Retrieval Mode: `{mode}`")
    
    # Display response time
    st.caption(f"⏱️ Response Time: {response_time:.2f}s")
    
    st.rerun()


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-container">
    <p>
        🚀 Powered by <strong>Retrieval-Augmented Generation (RAG)</strong> | 
        <span style='font-size: 0.8rem;'>sentence-transformers • ChromaDB • FastAPI • Streamlit</span>
    </p>
    <p style='margin-top: 0.5rem;'>
        Made with ❤️ for college admission seekers
    </p>
</div>
""", unsafe_allow_html=True)
"""
app.py — Industry-Standard Streamlit Chat UI for College Admission Chatbot

Run:  streamlit run frontend/app.py
"""

import sys
import os
import time
import requests
import streamlit as st
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="College Admission Assistant | AdmissionBot AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "College Admission Chatbot powered by RAG technology"}
)

# ── Professional CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main {
        background: #ffffff;
    }
    
    /* Header Styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 0;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    
    .header-content {
        color: white;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin: 0;
    }
    
    .header-subtitle {
        font-size: 0.95rem;
        opacity: 0.95;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    /* Chat Container */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Message Styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
        word-wrap: break-word;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    .assistant-message {
        background: #f8f9fa;
        color: #2d3748;
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        word-wrap: break-word;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Source Badge */
    .source-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #f0f2f5 100%);
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    .source-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 0.75rem;
        margin: 4px 4px 4px 0;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
    }
    
    .relevance-bar {
        height: 6px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 3px;
        margin-top: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar */
    [data-testid="sidebar"] {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%);
    }
    
    [data-testid="sidebar"] .css-1d391kg {
        padding: 1.5rem 1rem;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.7rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Input Box */
    .stChatInputContainer {
        padding: 1.5rem 0;
        background: white;
        border-top: 1px solid #e2e8f0;
    }
    
    .stChatInput input {
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stChatInput input:focus {
        border: 2px solid #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #f8f9fa !important;
        border-radius: 8px !important;
    }
    
    /* Stats Badge */
    .stats-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    /* Footer */
    .footer-container {
        text-align: center;
        padding: 2rem 1rem;
        border-top: 1px solid #e2e8f0;
        color: #718096;
        font-size: 0.85rem;
        margin-top: 3rem;
    }
    
    .footer-link {
        color: #667eea;
        text-decoration: none;
        font-weight: 600;
    }
    
    .footer-link:hover {
        text-decoration: underline;
    }
    
    /* Loading Animation */
    .loading-pulse {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
API_URL = os.getenv("API_URL", "http://localhost:8000")
USE_DIRECT = True   # Set False to call FastAPI; True to call pipeline directly

SUGGESTED_QUESTIONS = [
    "📅 What is the last date to apply?",
    "💰 What is the B.Tech fee per year?",
    "✅ What are the eligibility criteria for MBA?",
    "📋 What documents are required for admission?",
    "🏠 Tell me about hostel facilities",
    "💼 What is the average placement package for CSE?",
]

# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None
if "response_time" not in st.session_state:
    st.session_state.response_time = 0


# ── Helper: Get Answer ────────────────────────────────────────────────────────
@st.cache_resource
def load_pipeline():
    """Load the RAG pipeline once on startup"""
    try:
        from backend.rag_pipeline import answer
        return answer
    except Exception as e:
        return None

def get_answer(question: str) -> dict:
    """Get answer from pipeline or API"""
    start_time = time.time()
    
    if USE_DIRECT:
        try:
            answer_fn = load_pipeline()
            if answer_fn is None:
                return {
                    "answer": "⚠️ Could not load pipeline. Run `python backend/ingest.py` first.",
                    "sources": [],
                    "mode": "error"
                }
            result = answer_fn(question)
            st.session_state.response_time = time.time() - start_time
            return result
        except Exception as e:
            return {
                "answer": f"⚠️ Error: {str(e)}",
                "sources": [],
                "mode": "error"
            }
    else:
        try:
            resp = requests.post(f"{API_URL}/ask", json={"question": question}, timeout=15)
            resp.raise_for_status()
            st.session_state.response_time = time.time() - start_time
            return resp.json()
        except Exception as e:
            return {"answer": f"⚠️ API Error: {str(e)}", "sources": [], "mode": "error"}


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🎓 **AdmissionBot AI**")
    st.markdown("*Intelligent College Admission Assistant*")
    st.markdown("---")
    
    st.markdown("#### 💡 **Quick Questions**")
    for q in SUGGESTED_QUESTIONS:
        if st.button(q, key=f"btn_{q}", use_container_width=True):
            st.session_state.pending_question = q
            st.rerun()
    
    st.markdown("---")
    st.markdown("#### ⚙️ **Settings**")
    
    col1, col2 = st.columns(2)
    with col1:
        show_sources = st.toggle("Sources", value=True, key="toggle_sources")
    with col2:
        show_mode = st.toggle("Mode", value=False, key="toggle_mode")
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.response_time = 0
        st.rerun()
    
    st.markdown("---")
    st.markdown("#### ℹ️ **About**")
    st.markdown(
        "This chatbot uses **Retrieval-Augmented Generation (RAG)** to provide "
        "accurate college admission information powered by sentence-transformers "
        "and ChromaDB vector database."
    )
    
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #718096; font-size: 0.8rem;'>"
        "<p>Built with ❤️ by Rahul Ramavath</p>"
        "<p>RAG Pipeline Project</p>"
        "</div>",
        unsafe_allow_html=True
    )


# ── Main Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-container">
    <div class="header-content">
        <div>
            <h1 class="header-title">🎓 College Admission Assistant</h1>
            <p class="header-subtitle">
                Get instant answers to all your college admission questions
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Chat History ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍🎓" if msg["role"] == "user" else "🎓"):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and show_sources and msg.get("sources"):
            with st.expander("📚 Retrieved Sources", expanded=False):
                for src in msg["sources"]:
                    rel = src.get("relevance", 0)
                    st.markdown(
                        f'<span class="source-badge">📄 {src["source"]}</span> '
                        f'Relevance: **{rel:.0%}**',
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f'<div class="relevance-bar" style="width:{rel*100:.0f}%"></div>',
                        unsafe_allow_html=True
                    )
                    st.markdown("")
        if msg["role"] == "assistant" and show_mode and msg.get("mode"):
            st.caption(f"🔧 Mode: `{msg['mode']}`")


# ── Handle Input ──────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask about admissions, fees, courses, hostel...")

# Use quick-question button if clicked
question = user_input or st.session_state.pending_question
if st.session_state.pending_question:
    st.session_state.pending_question = None

if question:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(question)

    # Get and show assistant response
    with st.chat_message("assistant", avatar="🎓"):
        with st.spinner("Searching knowledge base..."):
            result = get_answer(question)

        answer_text = result.get("answer", "Sorry, I couldn't find an answer.")
        sources = result.get("sources", [])
        mode = result.get("mode", "")

        # Typewriter effect
        placeholder = st.empty()
        displayed = ""
        for char in answer_text:
            displayed += char
            placeholder.markdown(displayed + "▌")
            time.sleep(0.008)
        placeholder.markdown(displayed)

        if show_sources and sources:
            with st.expander("📚 Retrieved Sources", expanded=False):
                for src in sources:
                    rel = src.get("relevance", 0)
                    st.markdown(
                        f'<span class="source-badge">📄 {src["source"]}</span> '
                        f'Relevance: **{rel:.0%}**',
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f'<div class="relevance-bar" style="width:{rel*100:.0f}%"></div>',
                        unsafe_allow_html=True
                    )
                    st.markdown("")

        if show_mode and mode:
            st.caption(f"🔧 Mode: `{mode}`")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer_text,
        "sources": sources,
        "mode": mode
    })

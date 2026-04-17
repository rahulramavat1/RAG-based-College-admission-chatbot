"""
app.py — Streamlit Chat UI for College Admission Chatbot

Run:  streamlit run frontend/app.py
"""

import sys
import os
import time
import requests
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="College Admission Chatbot",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stChatMessage { border-radius: 12px; margin-bottom: 8px; }
    .source-badge {
        display: inline-block;
        background: #e8f4fd;
        color: #1a73e8;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.75rem;
        margin: 2px;
    }
    .relevance-bar {
        height: 4px;
        background: linear-gradient(90deg, #1a73e8, #34a853);
        border-radius: 2px;
    }
    .chip {
        display: inline-block;
        background: #f1f3f4;
        border: 1px solid #dadce0;
        border-radius: 16px;
        padding: 4px 12px;
        font-size: 0.82rem;
        margin: 3px;
        cursor: pointer;
        color: #3c4043;
    }
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
API_URL = os.getenv("API_URL", "http://localhost:8000")
USE_DIRECT = True   # Set False to call FastAPI; True to call pipeline directly

SUGGESTED_QUESTIONS = [
    "What is the last date to apply?",
    "What is the B.Tech fee per year?",
    "What are the eligibility criteria for MBA?",
    "What documents are required for admission?",
    "Tell me about hostel facilities",
    "What is the average placement package for CSE?",
]

# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# ── Helper: Get Answer ────────────────────────────────────────────────────────
def get_answer(question: str) -> dict:
    if USE_DIRECT:
        # Call pipeline directly (no server needed)
        try:
            from backend.rag_pipeline import answer
            return answer(question)
        except Exception as e:
            return {
                "answer": f"⚠️ Could not load pipeline. Run `python backend/ingest.py` first.\n\nError: {e}",
                "sources": [],
                "mode": "error"
            }
    else:
        # Call FastAPI backend
        try:
            resp = requests.post(f"{API_URL}/ask", json={"question": question}, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"answer": f"API error: {e}", "sources": [], "mode": "error"}


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/graduation-cap.png", width=64)
    st.title("🎓 AdmissionBot")
    st.caption("Powered by RAG + sentence-transformers")
    st.divider()

    st.markdown("**💡 Quick Questions**")
    for q in SUGGESTED_QUESTIONS:
        if st.button(q, key=f"btn_{q}", use_container_width=True):
            st.session_state.pending_question = q

    st.divider()
    st.markdown("**⚙️ Settings**")
    show_sources = st.toggle("Show source chunks", value=True)
    show_mode = st.toggle("Show retrieval mode", value=False)

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("Built by Rahul Ramavath · RAG Pipeline Project")


# ── Main Header ───────────────────────────────────────────────────────────────
st.markdown("## 🎓 College Admission Assistant")
st.caption("Ask me anything about admissions, fees, eligibility, courses, hostel, or placements.")
st.divider()

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

import requests
import streamlit as st

import config

API = config.API_URL

st.set_page_config(page_title="OSTutor", layout="wide")

try:
    health = requests.get(f"{API}/health", timeout=(5, 30)).json()
except Exception:
    st.error(f"Backend is not running at {API}. Start the project with run.bat.")
    st.stop()

SESSION_ID = "streamlit_user"

if "current_conv_id" not in st.session_state:
    st.session_state.current_conv_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []


def load_conversations():
    try:
        return requests.get(f"{API}/conversations", params={"session_id": SESSION_ID}, timeout=5).json()
    except Exception:
        return []


def switch_conversation(conv_id):
    st.session_state.current_conv_id = conv_id
    try:
        msgs = requests.get(f"{API}/conversations/{conv_id}", timeout=5).json()
        st.session_state.messages = msgs
    except Exception:
        st.session_state.messages = []


with st.sidebar:
    if st.button("+ New Chat", use_container_width=True, type="primary"):
        st.session_state.current_conv_id = None
        st.session_state.messages = []
        st.rerun()

    st.markdown("### Chat History")
    convs = load_conversations()

    if convs:
        for c in convs:
            cid = c["id"]
            title = c.get("title") or "New conversation"
            is_active = (cid == st.session_state.current_conv_id)
            btn_label = f"▸ {title}" if is_active else title
            if st.button(btn_label, key=f"conv_{cid}", use_container_width=True):
                switch_conversation(cid)
                st.rerun()
    else:
        st.caption("No previous chats yet.")

    st.markdown("---")
    if convs and st.button("Clear All History", use_container_width=True):
        try:
            requests.delete(f"{API}/conversations", params={"session_id": SESSION_ID}, timeout=5)
        except Exception:
            pass
        st.session_state.current_conv_id = None
        st.session_state.messages = []
        st.rerun()


st.title("OSTutor")
st.caption("Operating Systems Study Assistant — Ask questions from the syllabus")

for msg in st.session_state.messages:
    role = msg.get("role", "user")
    content = msg.get("content", "")
    sources = msg.get("sources", [])

    with st.chat_message(role):
        st.markdown(content)
        if role == "assistant" and sources:
            with st.expander(f"Sources ({len(sources)})"):
                for i, s in enumerate(sources, 1):
                    sec = s.get("section") or s.get("topic") or "General"
                    src = s.get("source") or s.get("file", "")
                    if s.get("page"):
                        src += f", p.{s['page']}"
                    snippet = s.get("snippet", "")
                    st.markdown(f"**[{i}] {sec}** *({src})*\n\n> {snippet}")

user_query = st.chat_input("Ask any Operating Systems question...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query, "sources": []})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Searching notes and generating answer..."):
            try:
                payload = {
                    "question": user_query,
                    "session_id": SESSION_ID,
                    "conv_id": st.session_state.current_conv_id,
                }
                res = requests.post(f"{API}/ask", json=payload, timeout=(5, 120)).json()
                answer_text = res.get("answer", "")
                sources_list = res.get("sources", [])
                st.session_state.current_conv_id = res.get("conv_id")

                st.markdown(answer_text)
                if sources_list:
                    with st.expander(f"Sources ({len(sources_list)})"):
                        for i, s in enumerate(sources_list, 1):
                            sec = s.get("section") or s.get("topic") or "General"
                            src = s.get("source") or s.get("file", "")
                            if s.get("page"):
                                src += f", p.{s['page']}"
                            snippet = s.get("snippet", "")
                            st.markdown(f"**[{i}] {sec}** *({src})*\n\n> {snippet}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer_text,
                    "sources": sources_list,
                })
            except Exception as e:
                st.error(f"Error: {e}")

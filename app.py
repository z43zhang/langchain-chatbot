from typing import Set
from datetime import datetime
from backend.rag_pipeline import run_llm
import streamlit as st
import io
import pytz

EST = pytz.timezone("America/New_York")

# ------------------ Page Setup ------------------
st.set_page_config(page_title="LangChain Chatbot", page_icon="🤖")

st.markdown("<h1 style='text-align: center;'>🤖 RAG-Powered Chatbot for LangChain Documentation</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: right;'>Developed by Zhonghao Zhang</p>", unsafe_allow_html=True)

# ------------------ Session State Initialization ------------------
if "chat_answers_history" not in st.session_state:
    st.session_state["chat_answers_history"] = []
if "user_prompt_history" not in st.session_state:
    st.session_state["user_prompt_history"] = []
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "timestamps" not in st.session_state:
    st.session_state["timestamps"] = []

# ------------------ Helper Functions ------------------
def create_sources_string(source_urls: Set[str]) -> str:
    if not source_urls:
        return ""
    sources_list = sorted(source_urls)
    return "sources:\n" + "\n".join(f"{i+1}. {src}" for i, src in enumerate(sources_list))

def format_ts(ts):
    try:
        if isinstance(ts, datetime):
            return ts.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        return f"[Invalid timestamp: {e}]"
    return "[N/A]"


# ------------------ Chat Rendering ------------------
USER_AVATAR = "🧑‍💻"
ASSISTANT_AVATAR = "🤖"

if st.session_state["timestamps"]:
    for user_query, generated_response, (user_ts, ai_ts) in zip(
        st.session_state["user_prompt_history"],
        st.session_state["chat_answers_history"],
        st.session_state["timestamps"]
    ):
        with st.chat_message("user", avatar=USER_AVATAR):
            st.write(user_query)
            st.caption(format_ts(user_ts))
        with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
            st.write(generated_response)
            st.caption(format_ts(ai_ts))

# ------------------ Chat Input ------------------
prompt = st.chat_input("Ask anything about LangChain")

if prompt:
    with st.spinner("Generating response..."):

        user_time = datetime.now(EST)

        # Run the full RAG pipeline
        generated_response = run_llm(
            query=prompt,
            chat_history=st.session_state["chat_history"]
        )

        assistant_time = datetime.now(EST)

        # Extract and format source URLs
        sources = {doc.metadata["source"] for doc in generated_response["source_documents"]}
        formatted_response = f"{generated_response['result']} \n\n {create_sources_string(sources)}"

        # Save to session state
        st.session_state["user_prompt_history"].append(prompt)
        st.session_state["chat_answers_history"].append(formatted_response)
        st.session_state["chat_history"].append(("human", prompt))
        st.session_state["chat_history"].append(("ai", generated_response["result"]))
        st.session_state["timestamps"].append((user_time, assistant_time))

        # Render latest messages
        with st.chat_message("user", avatar=USER_AVATAR):
            st.write(prompt)
            st.caption(format_ts(user_time))
        with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
            st.write(formatted_response)
            st.caption(format_ts(assistant_time))

# ------------------ Reset & Download Buttons ------------------
if st.session_state["chat_answers_history"]:  # Only show if chat has started

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Reset Chat", key="reset_btn"):
            st.session_state["chat_answers_history"] = []
            st.session_state["user_prompt_history"] = []
            st.session_state["chat_history"] = []
            st.session_state["timestamps"] = []
            st.rerun()

    with col2:
        history_text = ""
        for user_msg, assistant_msg, (user_ts, ai_ts) in zip(
            st.session_state["user_prompt_history"],
            st.session_state["chat_answers_history"],
            st.session_state["timestamps"]
        ):
            history_text += f"User ({format_ts(user_ts)}): {user_msg}\n"
            history_text += f"Assistant ({format_ts(ai_ts)}): {assistant_msg}\n\n"

        buffer = io.BytesIO(history_text.encode("utf-8"))

        st.download_button(
            label="🖨️ Download",
            data=buffer,
            file_name="chat_history.txt",
            mime="text/plain",
            key="download_btn"
        )


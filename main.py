from typing import Set
from datetime import datetime
from backend.core import run_llm
import streamlit as st

# ------------------ Page Setup ------------------
st.set_page_config(page_title="LangChain Chatbot", page_icon="🧠")

# Centered title header
st.markdown("<h1 style='text-align: center;'>LangChain Assistant 🤖</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: right;'>Developed by Zhonghao Zhang</p>", unsafe_allow_html=True)

# Custom Avatars
USER_AVATAR = "🧑‍💻"
ASSISTANT_AVATAR = "🤖"

# ------------------ Session State Initialization ------------------
# Initialize chat history and metadata for persistence
if "chat_answers_history" not in st.session_state:
    st.session_state["chat_answers_history"] = []
if "user_prompt_history" not in st.session_state:
    st.session_state["user_prompt_history"] = []
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "timestamps" not in st.session_state:
    st.session_state["timestamps"] = []  # Timestamp for each turn

# ------------------ Helper Functions ------------------

# Format a set of source URLs into a numbered list
def create_sources_string(source_urls: Set[str]) -> str:
    if not source_urls:
        return ""
    sources_list = sorted(source_urls)
    return "sources:\n" + "\n".join(f"{i+1}. {src}" for i, src in enumerate(sources_list))

# # Convert timestamp to human-readable string format
def format_ts(ts):
    try:
        if isinstance(ts, datetime):
            return ts.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        return f"[Invalid timestamp: {e}]"
    return "[N/A]"

# ------------------ Render Previous Chat History ------------------

# If chat history exists, display past interactions with timestamps
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

# ------------------ Chat Input & Processing ------------------

# Show input box for user's next prompt
prompt = st.chat_input("Ask anything about LangChain")

if prompt:
    with st.spinner("Generating response..."):
        user_time = datetime.now()

        # Run the full RAG pipeline with chat history
        generated_response = run_llm(
            query=prompt,
            chat_history=st.session_state["chat_history"]
        )

        assistant_time = datetime.now()

        # Extract and format source URLs
        sources = {doc.metadata["source"] for doc in generated_response["source_documents"]}
        formatted_response = (
            f"{generated_response['result']} \n\n {create_sources_string(sources)}"
        )

        # ------------------ Save Current Turn ------------------

        st.session_state["user_prompt_history"].append(prompt)
        st.session_state["chat_answers_history"].append(formatted_response)
        st.session_state["chat_history"].append(("human", prompt))
        st.session_state["chat_history"].append(("ai", generated_response["result"]))
        st.session_state["timestamps"].append((user_time, assistant_time))

        # ------------------ Render Latest Turn ------------------

        with st.chat_message("user", avatar=USER_AVATAR):
            st.write(prompt)
            st.caption(format_ts(user_time))
        with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
            st.write(formatted_response)
            st.caption(format_ts(assistant_time))

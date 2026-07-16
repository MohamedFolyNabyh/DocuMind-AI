import uuid
import requests
import streamlit as st

# ==========================
# Configuration
# ==========================

API_URL = r"https://fictional-space-halibut-r4qpvq9gxjvcpwvp-8000.app.github.dev/chat/"
UPLOAD_URL = r"https://fictional-space-halibut-r4qpvq9gxjvcpwvp-8000.app.github.dev/upload/"

st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📄",
    layout="wide"
)

# ==========================
# Session State
# ==========================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# ==========================
# Sidebar
# ==========================

with st.sidebar:

    st.title("Saudi Tender Agent")

    st.write(f"**Session ID**")
    st.code(st.session_state.session_id)

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload Tender PDF",
        type=["pdf"]
    )

    if st.button("Upload PDF"):

        if uploaded_file is None:
            st.warning("Please select a PDF.")

        else:

            with st.spinner("Uploading..."):

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file,
                        "application/pdf"
                    )
                }

                response = requests.post(
                    UPLOAD_URL,
                    files=files
                )
                st.write(response.status_code)
                st.write(response.text)

                if response.status_code == 200:
                    st.session_state.source = uploaded_file.name

                    st.success("PDF uploaded successfully.")

                else:
                    st.write("Status:", response.status_code)
                    st.write("Response:", response.text)

                    st.error(response.text)

    st.divider()

    if st.button("Clear Chat"):

        st.session_state.messages = []

        st.rerun()

# ==========================
# Main Page
# ==========================

st.title("📄 DocuMind AI")

st.caption("Upload PDF documents and chat with them using AI")

# Display previous messages

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# Chat input

question = st.chat_input("Ask your question...")

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            response = requests.post(
                API_URL,
                json={
                    "session_id": st.session_state.session_id,
                    "question": question,
                    "source": st.session_state.source
                }
            )


            if response.status_code == 200:

                answer = response.json()["answer"]

            else:

                answer = response.text

            st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
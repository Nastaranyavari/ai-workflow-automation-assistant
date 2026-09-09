import requests
import streamlit as st


st.set_page_config(
    page_title="AI Workflow Automation Assistant",
    page_icon="🤖",
)


st.title("AI Workflow Automation Assistant")

st.write(
    "Upload a PDF, describe what you want, and let the AI Agent handle it."
)


uploaded_file = st.file_uploader(
    "Upload a PDF",
    type=["pdf"],
)


message = st.text_area(
    "What would you like the assistant to do?",
    placeholder="مثلاً: این فایل را خلاصه کن و خلاصه را در دیتابیس ذخیره کن.",
)


if st.button("Run Agent"):

    if not message.strip():
        st.error("Please enter a request.")

    else:
        st.info("Processing...")

        try:
            files = None

            if uploaded_file:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf",
                    )
                }

            data = {
                "message": message,
                "session_id": "streamlit-demo",
            }

            response = requests.post(
                "http://127.0.0.1:8000/assistant",
                data=data,
                files=files,
                timeout=120,
            )

            response.raise_for_status()

            result = response.json()

            st.success(
                f"Status: {result.get('status', 'unknown')}"
            )

            st.subheader("Result")

            st.write(
                result.get(
                    "response",
                    "No response returned."
                )
            )

        except requests.RequestException as exc:
            st.error(f"API request failed: {exc}")
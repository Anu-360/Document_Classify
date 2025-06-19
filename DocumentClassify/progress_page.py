def run_progress_page():
    import time
    import fitz
    import google.generativeai as genai
    from datetime import datetime
    import streamlit as st

    st.title("📄 AI Document Processing Workflow")
    st.markdown("Watch documents get Ingested → Extracted → Classified → Routed.")

    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
    except KeyError:
        st.error("GEMINI_API_KEY not found in secrets.toml.")
        return

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    document_text = ""

    if uploaded_file:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf:
            for page in pdf:
                document_text += page.get_text()
        st.success("Text extracted successfully.")

        if not document_text.strip():
            st.warning("No text found in PDF.")
            return
    else:
        return

    # Init workflow
    if "workflow" not in st.session_state:
        st.session_state.workflow = {
            "Ingested": {"done": False, "timestamp": "", "details": "File received"},
            "Extracted": {"done": False, "timestamp": "", "details": ""},
            "Classified": {"done": False, "timestamp": "", "details": ""},
            "Routed": {"done": False, "timestamp": "", "details": ""}
        }
        st.session_state.processing_active = False

    # Show progress
    steps = list(st.session_state.workflow.keys())
    cols = st.columns(len(steps))
    for i, step in enumerate(steps):
        with cols[i]:
            if st.session_state.workflow[step]["done"]:
                st.success(f"**{step}** ✅")
            else:
                st.info(f"**{step}** ⏳")

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("▶️ Start Workflow", disabled=st.session_state.processing_active):
            st.session_state.processing_active = True
            for s in steps:
                st.session_state.workflow[s] = {"done": False, "timestamp": "", "details": ""}
            st.rerun()

    with col2:
        if st.button("🔁 Reset Workflow"):
            st.session_state.processing_active = False
            for step in steps:
                st.session_state.workflow[step] = {"done": False, "timestamp": "", "details": ""}
            st.rerun()

    with col3:
        if st.button("🔙 Back to Landing Page"):
            st.session_state.page = "status"
            st.rerun()

    # Execute workflow
    if st.session_state.processing_active:
        for step in steps:
            if not st.session_state.workflow[step]["done"]:
                time.sleep(2)
                st.session_state.workflow[step]["done"] = True
                st.session_state.workflow[step]["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if step == "Extracted":
                    st.session_state.workflow[step]["details"] = f"Text length: {len(document_text)}"
                elif step == "Classified":
                    with st.spinner("Calling Gemini..."):
                        model = genai.GenerativeModel("models/gemini-2.5-flash-preview-05-20")
                        response = model.generate_content(f"What is the type of this document?\n\n{document_text[:3000]}")
                        st.session_state.workflow[step]["details"] = f"Gemini classified as: {response.text.strip()}"
                elif step == "Routed":
                    st.session_state.workflow[step]["details"] = "Sent to appropriate department."
                st.rerun()

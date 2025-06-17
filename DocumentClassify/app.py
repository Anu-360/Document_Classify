import os
import pytesseract
import streamlit as st
from mail_box import run_mailbox_page
from utils import process_and_display_file

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
 
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'jpg', 'jpeg', 'png', 'gif'}
 
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
def main():
    st.set_page_config(page_title="Document Ingestion System", layout="wide")
 
    if "page" not in st.session_state:
        st.session_state.page = "home"
 
    if st.session_state.page == "home":
        st.title("Document Ingestion and Extraction")
 
        col1, col2 = st.columns([5, 1])
        with col2:
            if st.button("📬 Connect Mailbox"):
                st.session_state.page = "mailbox"
                st.experimental_rerun()
 
        st.header("Upload Documents")
        uploaded_files = st.file_uploader("Choose files", type=list(ALLOWED_EXTENSIONS), accept_multiple_files=True)
 
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if allowed_file(uploaded_file.name):
                    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.success(f"Uploaded: {uploaded_file.name}")
                    process_and_display_file(file_path, uploaded_file.name)
                else:
                    st.warning(f"Unsupported file type: {uploaded_file.name}")
 
    elif st.session_state.page == "mailbox":
        run_mailbox_page()
 
if __name__ == "__main__":
    main()
 
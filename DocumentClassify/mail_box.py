import streamlit as st
import imaplib
import email
import os
from utils import process_and_display_file  # ✅ Import from utils, not app
 
UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
 
def save_attachment(msg, download_folder):
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        filename = part.get_filename()
        if filename:
            filepath = os.path.join(download_folder, filename)
            with open(filepath, 'wb') as f:
                f.write(part.get_payload(decode=True))
            return filename
    return None
 
def run_mailbox_page():
    st.title("📬 Connect Your Mailbox")
    st.markdown("Provide your email credentials to fetch document attachments.")
 
    email_user = st.text_input("Email", key="email_user")
    email_pass = st.text_input("Password", type="password", key="email_pass")
 
    if st.button("🔐 Connect"):
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(email_user, email_pass)
            mail.select('inbox')
            result, data = mail.search(None, 'ALL')
            email_ids = data[0].split()
            fetched_any = False
 
            for email_id in email_ids[-10:]:  # Fetch latest 10
                result, msg_data = mail.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                filename = save_attachment(msg, UPLOAD_FOLDER)
                if filename:
                    fetched_any = True
                    st.success(f"📎 Attachment saved: {filename}")
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    process_and_display_file(file_path, filename)
 
            mail.logout()
            if not fetched_any:
                st.warning("No attachments found in recent emails.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
 
    if st.button("⬅ Back to Home"):
        st.session_state.page = "home"
        st.rerun()
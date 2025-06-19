import streamlit as st
import json
import os
import pandas as pd

LOG_FILE = "document_log.json"

def load_log():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        return json.load(f)

def display_status_table(log_data):
    if not log_data:
        st.info("No documents have been processed yet.")
        return

    table_data = []
    for doc in sorted(log_data, key=lambda x: x["last_updated"], reverse=True):
        table_data.append([
            doc["filename"],
            doc.get("type", "Pending"),
            doc["status"],
            doc["last_updated"]
        ])

    st.table(pd.DataFrame(table_data, columns=["Name", "Type", "Status", "Last Updated"]))

def run_status_page():
    st.title("📄 Recently Processed Documents")

    log_data = load_log()
    display_status_table(log_data)

    st.markdown("---")
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("📤 Go to Upload Page"):
            st.session_state.page = "upload"
            st.rerun()

    with col2:
        if st.button("📈 Live Progress"):
            st.session_state.page = "progress"
            st.rerun()


import os
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import docx
import pandas as pd
import streamlit as st
import json
import re
from datetime import datetime
from embedding_utils import classify_document

# File to track document processing status
LOG_FILE = "document_log.json"

# Extract text based on file type
def extract_text(file_path, filename):
    if filename.endswith(('jpg', 'jpeg', 'png', 'gif')):
        return pytesseract.image_to_string(Image.open(file_path))

    elif filename.endswith('.pdf'):
        try:
            with fitz.open(file_path) as doc:
                return "".join([page.get_text() for page in doc])
        except Exception as e:
            st.error(f"Error reading PDF file: {str(e)}")
            return ""

    elif filename.endswith('.docx'):
        try:
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            st.error(f"Error reading Word file: {str(e)}")
            return ""

    elif filename.endswith(('.xls', '.xlsx')):
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            return df.to_string(index=False)
        except Exception as e:
            st.error(f"Error reading Excel file: {str(e)}")
            return ""

    else:
        return "Unsupported file type."

# Update document status in the log
def update_document_log(filename, doc_type, status):
    log_entry = {
        "filename": filename,
        "type": doc_type,
        "status": status,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    existing = next((d for d in data if d["filename"] == filename), None)
    if existing:
        existing.update(log_entry)
    else:
        data.append(log_entry)

    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Main processing function
def process_and_display_file(file_path, filename):
    st.subheader(f"📄 {filename}")

    # Step 1: Extract
    extracted_text = extract_text(file_path, filename)
    update_document_log(filename, "Pending", "Ingested → Extracted")

    st.markdown("**📝 Extracted Text:**")
    st.write(extracted_text)

    # Step 2: Classify using Gemini
    st.markdown("**🧠 Document Classification Summary:**")
    try:
        result_text = classify_document(extracted_text)

        if result_text.startswith("ERROR::"):
            raise Exception(result_text.replace("ERROR::", ""))

        # ✅ Remove markdown code block formatting if present
        if result_text.strip().startswith("```"):
            result_text = re.sub(r"```(?:json)?", "", result_text).strip("` \n")

        classification = json.loads(result_text)

        doc_type = classification.get("type", "Unknown")
        confidence = float(classification.get("confidence", 0.0))
        reason = classification.get("reason", "No reason provided.")

        update_document_log(filename, doc_type, "Classified → Routed")

        st.success(f"📌 This document is classified as **{doc_type.upper()}** with confidence **{confidence:.2f}**.")
        st.info(f"🧾 Reason: {reason}")

    except json.JSONDecodeError:
        st.error("❌ Gemini response is not valid JSON. Raw response:")
        st.code(result_text)
    except Exception as e:
        st.warning(f"Gemini classification failed: {str(e)}")


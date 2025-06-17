import os
import pytesseract
from PIL import Image
import spacy
import fitz  # PyMuPDF
import docx
import pandas as pd  # For reading Excel files
import streamlit as st
from embedding_utils import add_document_to_pinecone, classify_document



# Load SpaCy English model
nlp = spacy.load("en_core_web_sm")

def extract_text(file_path, filename):
    if filename.endswith(('jpg', 'jpeg', 'png', 'gif')):
        return pytesseract.image_to_string(Image.open(file_path))

    elif filename.endswith('.pdf'):
        with fitz.open(file_path) as doc:
            return "".join([page.get_text() for page in doc])

    elif filename.endswith('.docx'):
        try:
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            st.error(f"Error reading Word file: {str(e)}")
            return ""

    elif filename.endswith(('.xls', '.xlsx')):
        try:
            df = pd.read_excel(file_path, engine='openpyxl')  # you can switch to 'xlrd' for .xls if needed
            return df.to_string(index=False)
        except Exception as e:
            st.error(f"Error reading Excel file: {str(e)}")
            return ""

    else:
        return "Unsupported file type."

def extract_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def process_and_display_file(file_path, filename):
    st.subheader(f"📄 {filename}")
    extracted_text = extract_text(file_path, filename)

    st.markdown("**📝 Extracted Text:**")
    st.write(extracted_text)

    # Classification
    st.markdown("**🧠 Document Classification Summary:**")
    try:
        classification = classify_document(extracted_text)
        if classification["matches"]:
            top_match = classification["matches"][0]
            doc_type = top_match["metadata"].get("type", "Unknown")
            score = top_match["score"]
            st.success(f"📌 This document is most likely a **{doc_type.upper()}** with a confidence score of **{score:.2f}**.")

            st.markdown("**🔍 Top 3 Similar Documents:**")
            for match in classification["matches"]:
                doc_type = match["metadata"].get("type", "Unknown")
                st.write(f"- **{doc_type}** | Score: {match['score']:.2f}")
        else:
            st.info("No similar documents found in Pinecone index.")
    except Exception as e:
        st.warning(f"Classification failed: {str(e)}")

    # Entity Extraction
    st.markdown("**🔎 Named Entities Found:**")
    for ent_text, ent_label in extract_entities(extracted_text):
        st.write(f"- {ent_text} ({ent_label})")

    # Add to Pinecone index
    add_document_to_pinecone(doc_id=filename, text=extracted_text, metadata={"filename": filename})





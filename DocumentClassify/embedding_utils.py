import os
import google.generativeai as genai

# Load Gemini API Key from environment variable or hardcoded fallback
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCtlMNvb3XOhcaUjQ8AIbxQfQkdUiHBr3Y")

# Configure Gemini with the key
genai.configure(api_key=GEMINI_API_KEY)

# Load Gemini model
model = genai.GenerativeModel("models/gemini-2.5-flash-preview-05-20")

# Classify document using Gemini LLM
def classify_document(text):
    prompt = f"""
You are a document classifier AI. Classify the document text into one of the following categories:

- Resume
- Invoice
- Letter
- Report
- Legal Document
- Financial Statement
- Educational Transcript
- Others

Respond ONLY in valid JSON format, no markdown, no extra explanation.

Format:
{{
  "type": "<document_type>",
  "confidence": "<confidence score between 0 and 1>",
  "reason": "<brief reason>"
}}

Here is the document content:
{text[:4000]}
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"ERROR::{str(e)}"

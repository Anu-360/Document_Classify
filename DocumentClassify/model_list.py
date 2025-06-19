import streamlit as st
import google.generativeai as genai

def run_model_explorer():
    st.title("🧠 Gemini API Model Explorer")

    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
    except KeyError:
        st.error("GEMINI_API_KEY not found in secrets.toml.")
        return

    try:
        models = list(genai.list_models())
        st.success(f"Found {len(models)} models")
        for model in models:
            st.markdown(f"**Model ID:** `{model.name}`")
            st.markdown(f"- Supported generation methods: {', '.join(model.supported_generation_methods)}")
            st.markdown("---")
    except Exception as e:
        st.error(f"Failed to list models: {e}")

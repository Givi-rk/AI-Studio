import os
import streamlit as st
from google import genai
from dotenv import load_dotenv
load_dotenv()
#GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
#client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
def get_api_key():
    return os.getenv("GEMINI_API_KEY")
# def get_genai_client():
#     if not GEMINI_API_KEY:
#         st.error("🔑 Gemini API key missing! Please configure it in your '.env' file.")
#         st.stop()
#     try:
#         return genai.Client(api_key=GEMINI_API_KEY)
#     except Exception as e:
#         st.error(f"Failed to initialize Gemini client:{e}")
#         st.stop()
# client=get_genai_client()

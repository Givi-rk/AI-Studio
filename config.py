import os
import streamlit as st
from google import genai
from dotenv import load_dotenv
from streamlit_cookies_controller import CookieController

load_dotenv()

def get_api_key():
    return os.getenv("GEMINI_API_KEY")

JWT_SECRET = os.getenv("JWT_SECRET")

cookie_controller = CookieController()
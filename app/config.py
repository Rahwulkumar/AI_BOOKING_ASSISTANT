"""
Configuration management for the AI Booking Assistant
Handles API keys, constants, and configuration settings
"""
import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Gemini API Configuration
def get_google_api_key():
    """Get Google Gemini API key from environment variable (.env) or Streamlit secrets (for cloud)"""
    # Prioritize .env file for local development
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        return api_key
    # Fallback to Streamlit secrets (for Streamlit Cloud deployment)
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except (KeyError, AttributeError):
        return ""

# Supabase Configuration
def get_supabase_config():
    """Get Supabase URL and key from Streamlit secrets (cloud) or .env (local)"""
    url = ""
    key = ""
    
    # On Streamlit Cloud, st.secrets is available - use it first
    try:
        if hasattr(st, 'secrets') and st.secrets:
            url_raw = st.secrets.get("SUPABASE_URL", "")
            key_raw = st.secrets.get("SUPABASE_KEY", "")
            # Sanitize: strip quotes and whitespace
            url = str(url_raw).strip().strip('"').strip("'")
            key = str(key_raw).strip().strip('"').strip("'")
    except (KeyError, AttributeError, TypeError):
        pass
    
    # Fallback to .env (for local development)
    if not url or not key:
        url = os.getenv("SUPABASE_URL", "").strip()
        key = os.getenv("SUPABASE_KEY", "").strip()
    
    return {"url": url, "key": key}

# Gmail SMTP Configuration
def get_email_config():
    """Get Gmail SMTP credentials from environment variables (.env) or Streamlit secrets (for cloud)"""
    # Prioritize .env file for local development
    email = os.getenv("GMAIL_ADDRESS")
    password = os.getenv("GMAIL_APP_PASSWORD")
    if email and password:
        return {"sender_email": email, "sender_password": password}
    # Fallback to Streamlit secrets (for Streamlit Cloud deployment)
    try:
        return {
            "sender_email": st.secrets["GMAIL_ADDRESS"],
            "sender_password": st.secrets["GMAIL_APP_PASSWORD"]
        }
    except (KeyError, AttributeError):
        return {"sender_email": "", "sender_password": ""}

# LLM Configuration
GEMINI_MODEL = "gemini-2.0-flash"  # Fast and free
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# RAG Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_CHUNKS = 8  # Increased from 5 for better context retrieval

# Memory Configuration
MAX_CONVERSATION_HISTORY = 25

# Booking Fields
REQUIRED_BOOKING_FIELDS = ["name", "email", "phone", "service", "date", "time"]

# Validation Patterns
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PHONE_MIN_LENGTH = 10
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


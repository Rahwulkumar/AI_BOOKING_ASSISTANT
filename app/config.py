"""
Configuration management for the AI Booking Assistant
Handles API keys, constants, and configuration settings
"""
import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq API Configuration
def get_groq_api_key():
    """Get Groq API key from Streamlit secrets or environment variable"""
    try:
        return st.secrets["GROQ_API_KEY"]
    except (KeyError, AttributeError):
        return os.getenv("GROQ_API_KEY", "")

# Supabase Configuration
def get_supabase_config():
    """Get Supabase URL and key from Streamlit secrets or environment variables"""
    try:
        return {
            "url": st.secrets["SUPABASE_URL"],
            "key": st.secrets["SUPABASE_KEY"]
        }
    except (KeyError, AttributeError):
        return {
            "url": os.getenv("SUPABASE_URL", ""),
            "key": os.getenv("SUPABASE_KEY", "")
        }

# Gmail SMTP Configuration
def get_email_config():
    """Get Gmail SMTP credentials from Streamlit secrets or environment variables"""
    try:
        return {
            "sender_email": st.secrets["GMAIL_ADDRESS"],
            "sender_password": st.secrets["GMAIL_APP_PASSWORD"]
        }
    except (KeyError, AttributeError):
        return {
            "sender_email": os.getenv("GMAIL_ADDRESS", ""),
            "sender_password": os.getenv("GMAIL_APP_PASSWORD", "")
        }

# LLM Configuration
GROQ_MODEL = "llama-3.1-70b-versatile"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# RAG Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_CHUNKS = 5

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


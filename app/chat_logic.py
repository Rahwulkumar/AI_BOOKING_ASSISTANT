import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.config import get_google_api_key, GEMINI_MODEL, MAX_CONVERSATION_HISTORY
from typing import List, Dict, Literal

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

def get_llm():
    if ChatGoogleGenerativeAI is None:
        raise ImportError("langchain-google-genai not installed. Run: pip install langchain-google-genai")
    api_key = get_google_api_key()
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env or Streamlit secrets")
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL, 
        google_api_key=api_key, 
        temperature=0.7,
        convert_system_message_to_human=True
    )

def detect_intent(user_message: str, conversation_history: List[Dict]) -> Literal["BOOKING", "QUERY"]:
    try:
        llm = get_llm()
        
        history_text = ""
        recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
        for msg in recent_history:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"
        
        booking_state = st.session_state.get("booking_state", {})
        if booking_state.get("intent") == "booking" and not booking_state.get("awaiting_confirmation"):
            return "BOOKING"
        
        system_prompt = """You are an intent classifier for a medical appointment booking system.
Classify user messages into two categories:
- BOOKING: User wants to make an appointment/booking (e.g., "I want to book", "Schedule an appointment", "I need to see a doctor")
- QUERY: User is asking questions about services, doctors, policies, hours, prices (e.g., "What are your hours?", "Do you have a cardiologist?", "How much does it cost?")

Respond with ONLY one word: either "BOOKING" or "QUERY"."""
        
        prompt = f"""Conversation history:
{history_text}

User message: {user_message}

Classify the intent. Respond with only: BOOKING or QUERY"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        intent = response.content.strip().upper()
        
        if "BOOKING" in intent:
            return "BOOKING"
        else:
            return "QUERY"
            
    except Exception as e:
        st.error(f"Error detecting intent: {str(e)}")
        return "QUERY"

def get_recent_messages(messages: List[Dict], max_messages: int = MAX_CONVERSATION_HISTORY) -> List[Dict]:
    if len(messages) <= max_messages:
        return messages
    return messages[-max_messages:]

def format_conversation_for_llm(messages: List[Dict]) -> str:
    formatted = []
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        formatted.append(f"{role}: {msg['content']}")
    return "\n".join(formatted)

def initialize_booking_state():
    if "booking_state" not in st.session_state:
        st.session_state.booking_state = {
            "name": None,
            "email": None,
            "phone": None,
            "service": None,
            "date": None,
            "time": None,
            "intent": None,
            "awaiting_confirmation": False
        }

def reset_booking_state():
    st.session_state.booking_state = {
        "name": None,
        "email": None,
        "phone": None,
        "service": None,
        "date": None,
        "time": None,
        "intent": None,
        "awaiting_confirmation": False
    }


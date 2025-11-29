"""
Booking flow: Slot filling, validation, and confirmation
"""
import streamlit as st
import re
from datetime import datetime, date
from typing import Dict, Optional, Tuple
from app.config import EMAIL_PATTERN, PHONE_MIN_LENGTH, DATE_FORMAT, TIME_FORMAT
from app.chat_logic import get_llm
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.tools import BookingPersistenceTool, EmailTool

def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format"""
    if not email:
        return False, "Email cannot be empty"
    if not re.match(EMAIL_PATTERN, email):
        return False, "Please provide a valid email address (e.g., example@email.com)"
    return True, ""

def validate_phone(phone: str) -> Tuple[bool, str]:
    """Validate phone number"""
    if not phone:
        return False, "Phone number cannot be empty"
    # Remove common separators
    digits_only = re.sub(r'[\s\-\(\)\+]', '', phone)
    if len(digits_only) < PHONE_MIN_LENGTH:
        return False, f"Please provide a valid phone number (at least {PHONE_MIN_LENGTH} digits)"
    return True, ""

def validate_date(date_str: str) -> Tuple[bool, str]:
    """Validate date format and ensure it's in the future"""
    if not date_str:
        return False, "Date cannot be empty"
    try:
        parsed_date = datetime.strptime(date_str, DATE_FORMAT).date()
        today = date.today()
        if parsed_date <= today:
            return False, "Please select a future date (format: YYYY-MM-DD, e.g., 2025-12-15)"
        return True, ""
    except ValueError:
        return False, "Please use date format YYYY-MM-DD (e.g., 2025-12-15)"

def validate_time(time_str: str) -> Tuple[bool, str]:
    """Validate time format"""
    if not time_str:
        return False, "Time cannot be empty"
    try:
        datetime.strptime(time_str, TIME_FORMAT)
        return True, ""
    except ValueError:
        return False, "Please use time format HH:MM (24-hour format, e.g., 14:30)"

def extract_field_from_message(message: str, field_name: str, conversation_history: list) -> Optional[str]:
    """
    Extract field value from user message using LLM
    Returns extracted value or None
    """
    try:
        llm = get_llm()
        
        # Format history
        history_text = ""
        for msg in conversation_history[-5:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_text += f"{role}: {msg['content']}\n"
        
        system_prompt = f"""You are extracting information from user messages for appointment booking.
Extract the {field_name} from the user's message. 
If the user provides the {field_name}, return ONLY the value, nothing else.
If the user doesn't provide it, return "NOT_FOUND"."""
        
        prompt = f"""Conversation:
{history_text}

User message: {message}

Extract the {field_name} from this message. Return only the value or "NOT_FOUND"."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        extracted = response.content.strip()
        
        if "NOT_FOUND" in extracted.upper() or not extracted:
            return None
        return extracted
        
    except Exception as e:
        st.error(f"Error extracting field: {str(e)}")
        return None

def get_missing_fields(booking_state: Dict) -> list:
    """Get list of missing required fields"""
    required_fields = ["name", "email", "phone", "service", "date", "time"]
    missing = [field for field in required_fields if not booking_state.get(field)]
    return missing

def get_next_field_prompt(field: str) -> str:
    """Get prompt to ask for a specific field"""
    prompts = {
        "name": "Great! What is your full name?",
        "email": "What is your email address?",
        "phone": "What is your phone number?",
        "service": "What type of service or consultation do you need? (e.g., Cardiology consultation, General checkup, Dermatology)",
        "date": "What is your preferred date? Please use format YYYY-MM-DD (e.g., 2025-12-15)",
        "time": "What time would you prefer? Please use format HH:MM (24-hour format, e.g., 14:30)"
    }
    return prompts.get(field, f"Please provide your {field}")

def collect_booking_info(user_message: str, conversation_history: list) -> Tuple[Dict, str]:
    """
    Collect booking information from user message
    Returns: (updated_booking_state, response_message)
    """
    booking_state = st.session_state.booking_state
    booking_state["intent"] = "booking"
    
    # Get missing fields
    missing_fields = get_missing_fields(booking_state)
    
    if not missing_fields:
        # All fields collected, move to confirmation
        return booking_state, ""
    
    # Try to extract current field from message
    current_field = missing_fields[0]
    
    # Extract value from message
    extracted_value = extract_field_from_message(user_message, current_field, conversation_history)
    
    if extracted_value:
        # Validate based on field type
        if current_field == "email":
            is_valid, error_msg = validate_email(extracted_value)
            if not is_valid:
                return booking_state, error_msg
        elif current_field == "phone":
            is_valid, error_msg = validate_phone(extracted_value)
            if not is_valid:
                return booking_state, error_msg
        elif current_field == "date":
            is_valid, error_msg = validate_date(extracted_value)
            if not is_valid:
                return booking_state, error_msg
        elif current_field == "time":
            is_valid, error_msg = validate_time(extracted_value)
            if not is_valid:
                return booking_state, error_msg
        
        # Save field
        booking_state[current_field] = extracted_value
        
        # Check if all fields collected
        remaining_missing = get_missing_fields(booking_state)
        if not remaining_missing:
            # All fields collected
            return booking_state, ""
        else:
            # Ask for next field
            next_field = remaining_missing[0]
            return booking_state, get_next_field_prompt(next_field)
    else:
        # Value not found, ask for it
        return booking_state, get_next_field_prompt(current_field)

def format_booking_summary(booking_state: Dict) -> str:
    """Format booking details for confirmation"""
    summary = f"""
Please confirm your booking details:

**Name:** {booking_state.get('name', 'N/A')}
**Email:** {booking_state.get('email', 'N/A')}
**Phone:** {booking_state.get('phone', 'N/A')}
**Service:** {booking_state.get('service', 'N/A')}
**Date:** {booking_state.get('date', 'N/A')}
**Time:** {booking_state.get('time', 'N/A')}

Is this information correct? Please confirm (yes/no)
    """
    return summary.strip()

def handle_booking_confirmation(user_response: str, booking_state: Dict) -> Tuple[bool, str, Optional[int]]:
    """
    Handle booking confirmation
    Returns: (success: bool, message: str, booking_id: Optional[int])
    """
    user_response_lower = user_response.lower().strip()
    
    if "yes" in user_response_lower or "confirm" in user_response_lower or "correct" in user_response_lower:
        # User confirmed, save booking
        try:
            booking_tool = BookingPersistenceTool()
            success, booking_id, message = booking_tool.execute(booking_state)
            
            if success and booking_id:
                # Send email
                email_tool = EmailTool()
                email_details = {
                    "name": booking_state.get("name"),
                    "booking_id": booking_id,
                    "service": booking_state.get("service"),
                    "date": booking_state.get("date"),
                    "time": booking_state.get("time")
                }
                email_success, email_msg = email_tool.execute(booking_state.get("email"), email_details)
                
                if email_success:
                    final_message = f"✅ Booking confirmed! Your booking ID is #{booking_id}. Confirmation email sent to {booking_state.get('email')}"
                else:
                    final_message = f"✅ Booking confirmed! Your booking ID is #{booking_id}. (Note: Confirmation email could not be sent: {email_msg})"
                
                # Reset booking state
                from app.chat_logic import reset_booking_state
                reset_booking_state()
                
                return True, final_message, booking_id
            else:
                return False, f"❌ {message}", None
                
        except Exception as e:
            return False, f"❌ Error processing booking: {str(e)}", None
    
    elif "no" in user_response_lower or "incorrect" in user_response_lower or "wrong" in user_response_lower:
        # User wants to correct
        return False, "What would you like to change? Please specify the field and the correct value.", None
    
    else:
        # Unclear response
        return False, "Please respond with 'yes' to confirm or 'no' to make changes.", None


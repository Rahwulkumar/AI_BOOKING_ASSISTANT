import streamlit as st
import re
from datetime import datetime, date, timedelta
from typing import Dict, Optional, Tuple, List
from app.config import EMAIL_PATTERN, PHONE_MIN_LENGTH, DATE_FORMAT, TIME_FORMAT
from app.chat_logic import get_llm
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.tools import BookingPersistenceTool, EmailTool
from db.database import get_database

MORNING_SLOTS = ["09:00", "10:00", "11:00", "12:00"]
AFTERNOON_SLOTS = ["13:00", "14:00", "15:00", "16:00"]
EVENING_SLOTS = ["17:00", "18:00", "19:00"]
ALL_TIME_SLOTS = MORNING_SLOTS + AFTERNOON_SLOTS + EVENING_SLOTS

def extract_services_from_pdfs() -> List[str]:
    try:
        if st.session_state.get("vector_store") is None:
            return get_default_services()
        
        from app.rag_pipeline import RAGPipeline
        rag_pipeline = RAGPipeline()
        context = rag_pipeline.get_context_for_query("List all doctors and their specialties with consultation fees")
        
        if "No relevant information" in context:
            return get_default_services()
        
        services = []
        lines = context.split('\n')
        
        current_doctor = None
        current_specialty = None
        current_fee = None
        
        for line in lines:
            line = line.strip()
            
            if 'Dr.' in line and '-' in line:
                parts = line.split('-')
                if len(parts) >= 2:
                    current_doctor = parts[0].strip()
                    current_specialty = parts[1].strip()
            
            if 'Fee:' in line or 'Consultation' in line:
                fee_match = re.search(r'\$(\d+)', line)
                if fee_match:
                    current_fee = f"${fee_match.group(1)}"
            
            if current_doctor and current_specialty and current_fee:
                service_name = f"{current_specialty} - {current_doctor} ({current_fee})"
                if service_name not in services:
                    services.append(service_name)
                current_doctor = None
                current_specialty = None
                current_fee = None
        
        if not services:
            return get_default_services()
        
        return services
        
    except Exception as e:
        st.error(f"Error extracting services: {str(e)}")
        return get_default_services()

def get_default_services() -> List[str]:
    return [
        "General Consultation",
        "Cardiology Consultation",
        "Dermatology Consultation",
        "Pediatrics Consultation",
        "Orthopedics Consultation",
        "Neurology Consultation",
        "Gynecology Consultation"
    ]

def get_booked_time_slots(selected_date: str) -> List[str]:
    try:
        db = get_database()
        query_result = db.client.table("bookings").select("time").eq("date", selected_date).execute()
        
        booked_times = []
        if query_result.data:
            for booking in query_result.data:
                time_str = booking.get("time", "")
                if time_str:
                    time_obj = datetime.strptime(time_str, "%H:%M:%S" if len(time_str) > 5 else "%H:%M")
                    normalized_time = time_obj.strftime("%H:%M")
                    booked_times.append(normalized_time)
        
        return booked_times
    except Exception as e:
        st.error(f"Error checking availability: {str(e)}")
        return []

def show_service_selector() -> Optional[str]:
    st.markdown("### 📋 Select Service")
    
    services = extract_services_from_pdfs()
    
    if "available_services" not in st.session_state:
        st.session_state.available_services = services
    
    selected_service = st.selectbox(
        "Choose the service you need:",
        options=services,
        key="service_selector"
    )
    
    if st.button("✅ Confirm Service", key="confirm_service"):
        return selected_service
    
    return None

def show_date_selector() -> Optional[str]:
    st.markdown("### 📅 Select Date")
    
    min_date = date.today() + timedelta(days=1)
    max_date = date.today() + timedelta(days=30)
    
    selected_date = st.date_input(
        "Choose your preferred date:",
        min_value=min_date,
        max_value=max_date,
        value=min_date,
        key="date_selector"
    )
    
    if st.button("✅ Confirm Date", key="confirm_date"):
        return selected_date.strftime("%Y-%m-%d")
    
    return None

def show_time_slot_selector(selected_date: str) -> Optional[str]:
    st.markdown("### ⏰ Select Time Slot")
    
    booked_slots = get_booked_time_slots(selected_date)
    available_count = len(ALL_TIME_SLOTS) - len(booked_slots)
    st.info(f"📊 {available_count} slots available out of {len(ALL_TIME_SLOTS)} on {selected_date}")
    
    selected_time = None
    
    st.markdown("**🌅 Morning (9 AM - 12 PM)**")
    cols = st.columns(len(MORNING_SLOTS))
    for idx, slot in enumerate(MORNING_SLOTS):
        with cols[idx]:
            is_booked = slot in booked_slots
            label = f"{slot}\n{'🔴 Booked' if is_booked else '🟢 Available'}"
            if st.button(label, key=f"morning_{slot}", disabled=is_booked, use_container_width=True):
                selected_time = slot
    
    st.markdown("**☀️ Afternoon (1 PM - 4 PM)**")
    cols = st.columns(len(AFTERNOON_SLOTS))
    for idx, slot in enumerate(AFTERNOON_SLOTS):
        with cols[idx]:
            is_booked = slot in booked_slots
            label = f"{slot}\n{'🔴 Booked' if is_booked else '🟢 Available'}"
            if st.button(label, key=f"afternoon_{slot}", disabled=is_booked, use_container_width=True):
                selected_time = slot
    
    st.markdown("**🌙 Evening (5 PM - 7 PM)**")
    cols = st.columns(len(EVENING_SLOTS))
    for idx, slot in enumerate(EVENING_SLOTS):
        with cols[idx]:
            is_booked = slot in booked_slots
            label = f"{slot}\n{'🔴 Booked' if is_booked else '🟢 Available'}"
            if st.button(label, key=f"evening_{slot}", disabled=is_booked, use_container_width=True):
                selected_time = slot
    
    return selected_time

def validate_email(email: str) -> Tuple[bool, str]:
    if not email:
        return False, "Email cannot be empty"
    if not re.match(EMAIL_PATTERN, email):
        return False, "Please provide a valid email address (e.g., example@email.com)"
    return True, ""

def validate_phone(phone: str) -> Tuple[bool, str]:
    if not phone:
        return False, "Phone number cannot be empty"
    digits_only = re.sub(r'[\s\-\(\)\+]', '', phone)
    if len(digits_only) < PHONE_MIN_LENGTH:
        return False, f"Please provide a valid phone number (at least {PHONE_MIN_LENGTH} digits)"
    return True, ""

def get_missing_fields(booking_state: Dict) -> list:
    required_fields = ["name", "email", "phone", "service", "date", "time"]
    missing = [field for field in required_fields if not booking_state.get(field)]
    return missing

def extract_field_from_message(message: str, field_name: str, conversation_history: list) -> Optional[str]:
    try:
        llm = get_llm()
        
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
        return None

def get_next_field_prompt(field: str) -> str:
    prompts = {
        "name": "Great! 😊 What's your full name?",
        "email": "Perfect! What's your email address?",
        "phone": "Got it! What's your phone number?",
        "service": "I'll show you our available services. Please select one.",
        "date": "When would you like to schedule your appointment? I'll show you a calendar.",
        "time": "What time works best for you? I'll show you the available time slots."
    }
    return prompts.get(field, f"Please provide your {field}")

def get_widget_instruction(field: str) -> str:
    instructions = {
        "service": "Please select a service from the dropdown above.",
        "date": "Please select a date from the calendar above.",
        "time": "Please select a time slot from the available options above."
    }
    return instructions.get(field, "")

def collect_booking_info_enhanced(user_message: str, conversation_history: list) -> Tuple[Dict, str, Optional[str]]:
    booking_state = st.session_state.booking_state
    booking_state["intent"] = "booking"
    
    missing_fields = get_missing_fields(booking_state)
    
    if not missing_fields:
        return booking_state, "", None
    
    current_field = missing_fields[0]
    
    if current_field in ["name", "email", "phone"]:
        extracted_value = extract_field_from_message(user_message, current_field, conversation_history)
        
        if extracted_value:
            if current_field == "email":
                is_valid, error_msg = validate_email(extracted_value)
                if not is_valid:
                    return booking_state, error_msg, None
            elif current_field == "phone":
                is_valid, error_msg = validate_phone(extracted_value)
                if not is_valid:
                    return booking_state, error_msg, None
            
            booking_state[current_field] = extracted_value
            
            remaining_missing = get_missing_fields(booking_state)
            if not remaining_missing:
                return booking_state, "", None
            else:
                next_field = remaining_missing[0]
                prompt = get_next_field_prompt(next_field)
                widget = next_field if next_field in ["service", "date", "time"] else None
                return booking_state, prompt, widget
        else:
            return booking_state, get_next_field_prompt(current_field), None
    
    elif current_field in ["service", "date", "time"]:
        prompt = get_next_field_prompt(current_field)
        return booking_state, prompt, current_field
    
    return booking_state, get_next_field_prompt(current_field), None

def format_booking_summary(booking_state: Dict) -> str:
    summary = f"""
✅ **Please confirm your booking details:**

👤 **Name:** {booking_state.get('name', 'N/A')}
📧 **Email:** {booking_state.get('email', 'N/A')}
📱 **Phone:** {booking_state.get('phone', 'N/A')}
🏥 **Service:** {booking_state.get('service', 'N/A')}
📅 **Date:** {booking_state.get('date', 'N/A')}
⏰ **Time:** {booking_state.get('time', 'N/A')}

Is this information correct? Please type **yes** to confirm or **no** to make changes.
    """
    return summary.strip()

def handle_booking_confirmation(user_response: str, booking_state: Dict) -> Tuple[bool, str, Optional[int]]:
    user_response_lower = user_response.lower().strip()
    
    if "yes" in user_response_lower or "confirm" in user_response_lower or "correct" in user_response_lower:
        try:
            booking_tool = BookingPersistenceTool()
            success, booking_id, message = booking_tool.execute(booking_state)
            
            if success and booking_id:
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
                    final_message = f"🎉 **Booking Confirmed!**\n\n✅ Your booking ID is **#{booking_id}**\n📧 Confirmation email sent to {booking_state.get('email')}\n\nThank you for choosing us! See you on {booking_state.get('date')} at {booking_state.get('time')}!"
                else:
                    final_message = f"🎉 **Booking Confirmed!**\n\n✅ Your booking ID is **#{booking_id}**\n\n⚠️ Note: Confirmation email could not be sent, but your booking is confirmed."
                
                from app.chat_logic import reset_booking_state
                reset_booking_state()
                
                return True, final_message, booking_id
            else:
                return False, f"❌ {message}", None
                
        except Exception as e:
            return False, f"❌ Error processing booking: {str(e)}", None
    
    elif "no" in user_response_lower or "incorrect" in user_response_lower or "wrong" in user_response_lower:
        from app.chat_logic import reset_booking_state
        reset_booking_state()
        return False, "No problem! Let's start over. Type 'I want to book an appointment' to begin again.", None
    
    else:
        return False, "Please type **yes** to confirm or **no** to cancel and start over.", None


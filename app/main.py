import os
import sys
import warnings
import logging

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'

warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', module='tensorflow')
warnings.filterwarnings('ignore', module='tf_keras')

logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('tf_keras').setLevel(logging.ERROR)

import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.chat_logic import (
    detect_intent, 
    initialize_booking_state, 
    get_recent_messages,
    reset_booking_state
)
from app.booking_flow import (
    collect_booking_info_enhanced,
    format_booking_summary, 
    handle_booking_confirmation,
    get_missing_fields,
    show_service_selector,
    show_date_selector,
    show_time_slot_selector
)
from app.tools import RAGTool
from app.rag_pipeline import RAGPipeline
from app.admin_dashboard import admin_dashboard_page
from app.user_bookings import user_bookings_page
from app.config import MAX_CONVERSATION_HISTORY

st.set_page_config(
    page_title="AI Doctor Appointment Booking Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize all session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    
    if "show_widget" not in st.session_state:
        st.session_state.show_widget = None
    
    if "last_uploaded_files" not in st.session_state:
        st.session_state.last_uploaded_files = []
    
    initialize_booking_state()

def chat_page():
    st.title("🏥 AI Doctor Appointment Booking Assistant")
    st.markdown("Ask questions about our services or book an appointment!")
    
    with st.sidebar:
        st.header("📄 Document Management")
        
        with st.expander("📚 Load Sample Documents", expanded=False):
            if st.button("Load Samples", use_container_width=True):
                try:
                    rag_pipeline = RAGPipeline()
                    sample_pdfs = [
                        "docs/doctors_list.pdf",
                        "docs/clinic_policies.pdf",
                        "docs/services_pricing.pdf"
                    ]
                    
                    chunks_count = 0
                    for pdf_path in sample_pdfs:
                        if os.path.exists(pdf_path):
                            with open(pdf_path, "rb") as f:
                                import io
                                pdf_bytes = f.read()
                                pdf_file_obj = io.BytesIO(pdf_bytes)
                                pdf_file_obj.name = os.path.basename(pdf_path)
                                chunks = rag_pipeline.process_pdfs([pdf_file_obj])
                                chunks_count += chunks
                    
                    if chunks_count > 0:
                        st.success(f"✅ Loaded {chunks_count} chunks!")
                        st.session_state.messages.append({"role": "assistant", "content": "I've loaded the sample clinic documents. You can now ask me about doctors, services, or pricing!"})
                        st.rerun()
                    else:
                        st.warning("⚠️ Sample PDFs not found.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        st.divider()
        
        st.subheader("Upload Your Documents")
        uploaded_files = st.file_uploader(
            "Upload PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload clinic documents to enable document-based answers. Files are processed automatically."
        )
        
        if uploaded_files:
            current_files = [f.name for f in uploaded_files]
            last_files = st.session_state.get("last_uploaded_files", [])
            
            if current_files != last_files:
                try:
                    with st.spinner(f"📄 Processing {len(uploaded_files)} PDF file(s)..."):
                        rag_pipeline = RAGPipeline()
                        total_chunks = rag_pipeline.process_pdfs(uploaded_files)
                        st.session_state.last_uploaded_files = current_files
                        st.success(f"✅ Processed {len(uploaded_files)} PDF(s) with {total_chunks} chunks!")
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": f"Great! I've processed {len(uploaded_files)} document(s) with {total_chunks} pieces of information. Ask me anything about the clinic! 😊"
                        })
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error processing PDFs: {str(e)}")
        
        st.divider()
        
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            reset_booking_state()
            st.rerun()
        
        if st.session_state.get("vector_store") is not None:
            st.success("✅ Documents loaded")
        else:
            st.info("ℹ️ No documents loaded")

    if not st.session_state.messages:
        st.markdown("""
        ### 👋 Welcome to Our AI Booking Assistant!
        
        I'm here to help you with:
        - 📅 **Book appointments** with our doctors (interactive & easy!)
        - ❓ **Answer questions** about services, doctors, and policies
        - 💰 **Check pricing** for consultations and procedures
        
        **Quick Actions:**
        """)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📅 Book Appointment", use_container_width=True):
                user_message = "I want to book an appointment"
                st.session_state.messages.append({"role": "user", "content": user_message})
                try:
                    response = process_user_message(user_message)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"I apologize, but I encountered an error: {str(e)}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.rerun()
        with col2:
            if st.button("👨‍⚕️ View Doctors", use_container_width=True):
                user_message = "Tell me about all the doctors"
                st.session_state.messages.append({"role": "user", "content": user_message})
                try:
                    response = process_user_message(user_message)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"I apologize, but I encountered an error: {str(e)}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.rerun()
        with col3:
            if st.button("💰 Check Pricing", use_container_width=True):
                user_message = "What are your consultation fees?"
                st.session_state.messages.append({"role": "user", "content": user_message})
                try:
                    response = process_user_message(user_message)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"I apologize, but I encountered an error: {str(e)}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.rerun()
        
        st.info("💡 **Tip:** Load sample PDFs from the sidebar to enable document-based answers!")

    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
    
    booking_state = st.session_state.booking_state
    show_widget = st.session_state.get("show_widget")
    
    if booking_state.get("intent") == "booking" and not booking_state.get("awaiting_confirmation"):
        missing_fields = get_missing_fields(booking_state)
        
        if missing_fields:
            current_field = missing_fields[0]
            
            if current_field == "service" and show_widget == "service":
                selected_service = show_service_selector()
                if selected_service:
                    booking_state["service"] = selected_service
                    st.session_state.show_widget = None
                    st.session_state.messages.append({"role": "user", "content": f"Selected: {selected_service}"})
                    
                    remaining = get_missing_fields(booking_state)
                    if remaining:
                        next_field = remaining[0]
                        from app.booking_flow import get_next_field_prompt
                        prompt = get_next_field_prompt(next_field)
                        st.session_state.messages.append({"role": "assistant", "content": prompt})
                        if next_field in ["service", "date", "time"]:
                            st.session_state.show_widget = next_field
                    else:
                        summary = format_booking_summary(booking_state)
                        booking_state["awaiting_confirmation"] = True
                        st.session_state.messages.append({"role": "assistant", "content": summary})
                    st.rerun()
            
            elif current_field == "date" and show_widget == "date":
                selected_date = show_date_selector()
                if selected_date:
                    booking_state["date"] = selected_date
                    st.session_state.show_widget = None
                    st.session_state.messages.append({"role": "user", "content": f"Selected: {selected_date}"})
                    
                    remaining = get_missing_fields(booking_state)
                    if remaining:
                        next_field = remaining[0]
                        from app.booking_flow import get_next_field_prompt
                        prompt = get_next_field_prompt(next_field)
                        st.session_state.messages.append({"role": "assistant", "content": prompt})
                        if next_field in ["service", "date", "time"]:
                            st.session_state.show_widget = next_field
                    else:
                        summary = format_booking_summary(booking_state)
                        booking_state["awaiting_confirmation"] = True
                        st.session_state.messages.append({"role": "assistant", "content": summary})
                    st.rerun()
            
            elif current_field == "time" and show_widget == "time":
                selected_date = booking_state.get("date", "")
                if selected_date:
                    selected_time = show_time_slot_selector(selected_date)
                    if selected_time:
                        booking_state["time"] = selected_time
                        st.session_state.show_widget = None
                        st.session_state.messages.append({"role": "user", "content": f"Selected: {selected_time}"})
                        
                        summary = format_booking_summary(booking_state)
                        booking_state["awaiting_confirmation"] = True
                        st.session_state.messages.append({"role": "assistant", "content": summary})
                        st.rerun()
    
    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                try:
                    response = process_user_message(prompt)
                    st.markdown(response)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    response = "I apologize, but I encountered an error. Please try again or contact support."
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Rerun if a widget needs to be shown (service, date, or time selector)
        if st.session_state.get("show_widget") in ["service", "date", "time"]:
            st.rerun()
        
        if len(st.session_state.messages) > MAX_CONVERSATION_HISTORY * 2:
            st.session_state.messages = st.session_state.messages[-MAX_CONVERSATION_HISTORY * 2:]

def process_user_message(user_message: str) -> str:
    booking_state = st.session_state.booking_state
    
    if booking_state.get("awaiting_confirmation"):
        success, message, booking_id = handle_booking_confirmation(user_message, booking_state)
        st.session_state.show_widget = None
        return message
    
    conversation_history = get_recent_messages(st.session_state.messages)
    intent = detect_intent(user_message, conversation_history)
    
    if intent == "BOOKING":
        booking_state, response, widget_type = collect_booking_info_enhanced(user_message, conversation_history)
        
        if widget_type:
            st.session_state.show_widget = widget_type
        
        missing_fields = get_missing_fields(booking_state)
        if not missing_fields:
            summary = format_booking_summary(booking_state)
            booking_state["awaiting_confirmation"] = True
            st.session_state.show_widget = None
            return summary
        else:
            return response
    
    else:
        try:
            rag_tool = RAGTool()
            response = rag_tool.execute(user_message, conversation_history)
            return response
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please ensure documents are loaded and API keys are configured."

def main():
    initialize_session_state()
    
    with st.sidebar:
        st.title("🏥 Navigation")
        page = st.radio(
            "Go to:",
            ["Chat", "Find My Booking", "Admin Dashboard"],
            index=0
        )
    
    if page == "Chat":
        chat_page()
    elif page == "Find My Booking":
        user_bookings_page()
    elif page == "Admin Dashboard":
        admin_dashboard_page()

if __name__ == "__main__":
    main()


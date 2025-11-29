"""
Main Streamlit application for AI Booking Assistant
"""
import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.chat_logic import (
    detect_intent, 
    initialize_booking_state, 
    get_recent_messages,
    reset_booking_state
)
from app.booking_flow import (
    collect_booking_info, 
    format_booking_summary, 
    handle_booking_confirmation,
    get_missing_fields
)
from app.tools import RAGTool
from app.rag_pipeline import RAGPipeline
from app.admin_dashboard import admin_dashboard_page
from app.config import MAX_CONVERSATION_HISTORY

# Page configuration
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
    
    initialize_booking_state()

def chat_page():
    """Main chat interface page"""
    st.title("🏥 AI Doctor Appointment Booking Assistant")
    st.markdown("Ask questions about our services or book an appointment!")
    
    # Sidebar for PDF upload
    with st.sidebar:
        st.header("📄 Document Management")
        
        # Option 1: Load sample PDFs
        st.subheader("Load Sample Documents")
        if st.button("📚 Load Sample PDFs", use_container_width=True):
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
                            chunks = rag_pipeline.process_pdfs([f])
                            chunks_count += chunks
                
                if chunks_count > 0:
                    st.success(f"✅ Knowledge base loaded with {chunks_count} chunks from sample documents!")
                else:
                    st.warning("⚠️ Sample PDFs not found. Please upload your own PDFs below.")
            except Exception as e:
                st.error(f"❌ Error loading sample PDFs: {str(e)}")
        
        st.divider()
        
        # Option 2: Upload custom PDFs
        st.subheader("Upload Your Documents")
        uploaded_files = st.file_uploader(
            "Upload PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload one or more PDF files containing clinic information"
        )
        
        if uploaded_files:
            try:
                with st.spinner(f"Processing {len(uploaded_files)} PDF file(s)..."):
                    rag_pipeline = RAGPipeline()
                    total_chunks = rag_pipeline.process_pdfs(uploaded_files)
                    st.success(f"✅ Processed {len(uploaded_files)} PDF(s) with {total_chunks} chunks!")
            except Exception as e:
                st.error(f"❌ Error processing PDFs: {str(e)}")
        
        st.divider()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            reset_booking_state()
            st.rerun()
        
        # Show current status
        if st.session_state.get("vector_store") is not None:
            st.success("✅ Documents loaded")
        else:
            st.info("ℹ️ No documents loaded")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process message
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = process_user_message(prompt)
                st.markdown(response)
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Trim history if too long
        if len(st.session_state.messages) > MAX_CONVERSATION_HISTORY * 2:
            st.session_state.messages = st.session_state.messages[-MAX_CONVERSATION_HISTORY * 2:]

def process_user_message(user_message: str) -> str:
    """
    Process user message: detect intent and route to appropriate handler
    Returns response string
    """
    booking_state = st.session_state.booking_state
    
    # Check if awaiting confirmation
    if booking_state.get("awaiting_confirmation"):
        success, message, booking_id = handle_booking_confirmation(user_message, booking_state)
        return message
    
    # Get conversation history
    conversation_history = get_recent_messages(st.session_state.messages)
    
    # Detect intent
    intent = detect_intent(user_message, conversation_history)
    
    if intent == "BOOKING":
        # Handle booking flow
        booking_state, response = collect_booking_info(user_message, conversation_history)
        
        # Check if all fields collected
        missing_fields = get_missing_fields(booking_state)
        if not missing_fields:
            # All fields collected, show summary and ask for confirmation
            summary = format_booking_summary(booking_state)
            booking_state["awaiting_confirmation"] = True
            return summary
        else:
            # Still collecting fields
            return response if response else get_next_field_prompt(missing_fields[0])
    
    else:
        # Handle general query with RAG
        try:
            rag_tool = RAGTool()
            response = rag_tool.execute(user_message, conversation_history)
            return response
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please ensure documents are loaded and API keys are configured."

def get_next_field_prompt(field: str) -> str:
    """Get prompt for next field"""
    prompts = {
        "name": "Great! What is your full name?",
        "email": "What is your email address?",
        "phone": "What is your phone number?",
        "service": "What type of service or consultation do you need?",
        "date": "What is your preferred date? (Format: YYYY-MM-DD)",
        "time": "What time would you prefer? (Format: HH:MM, 24-hour)"
    }
    return prompts.get(field, f"Please provide your {field}")

def instructions_page():
    """Instructions and setup page"""
    st.title("📖 Instructions & Setup")
    st.markdown("---")
    
    st.markdown("""
    ## 🔧 Setup Instructions
    
    ### 1. Install Dependencies
    
    ```bash
    pip install -r requirements.txt
    ```
    
    ### 2. Configure API Keys
    
    You need to set up the following in `.streamlit/secrets.toml`:
    
    ```toml
    GROQ_API_KEY = "your-groq-api-key"
    SUPABASE_URL = "your-supabase-url"
    SUPABASE_KEY = "your-supabase-key"
    GMAIL_ADDRESS = "your-email@gmail.com"
    GMAIL_APP_PASSWORD = "your-app-password"
    ```
    
    #### Getting API Keys:
    
    **Groq API Key:**
    - Visit [Groq Console](https://console.groq.com/keys)
    - Create a new API key
    - Copy and add to secrets.toml
    
    **Supabase:**
    - Visit [Supabase](https://supabase.com)
    - Create a new project
    - Go to Settings > API
    - Copy Project URL and anon/public key
    - Run the SQL script in Supabase SQL Editor to create tables:
    
    ```sql
    CREATE TABLE customers (
        customer_id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    );
    
    CREATE TABLE bookings (
        id SERIAL PRIMARY KEY,
        customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
        booking_type TEXT NOT NULL,
        date DATE NOT NULL,
        time TIME NOT NULL,
        status TEXT DEFAULT 'confirmed',
        created_at TIMESTAMP DEFAULT NOW()
    );
    
    CREATE INDEX idx_customer_email ON customers(email);
    CREATE INDEX idx_booking_date ON bookings(date);
    CREATE INDEX idx_customer_id ON bookings(customer_id);
    ```
    
    **Gmail App Password:**
    - Enable 2-factor authentication on your Gmail account
    - Go to Google Account > Security > App passwords
    - Generate a new app password for "Mail"
    - Use this password (not your regular Gmail password)
    
    ### 3. Run the Application
    
    ```bash
    streamlit run app/main.py
    ```
    
    ## 📚 How to Use
    
    ### Chat Interface
    
    1. **Load Documents**: Upload PDFs or load sample PDFs from the sidebar
    2. **Ask Questions**: Ask about services, doctors, policies, hours, etc.
    3. **Book Appointment**: Say "I want to book an appointment" to start booking
    
    ### Booking Flow
    
    1. The system will ask for:
       - Your full name
       - Email address
       - Phone number
       - Service/consultation type
       - Preferred date (YYYY-MM-DD)
       - Preferred time (HH:MM, 24-hour format)
    
    2. Review the summary and confirm
    
    3. Receive booking confirmation with ID and email
    
    ### Admin Dashboard
    
    - View all bookings
    - Search by name or email
    - Export to CSV
    
    ## ⚠️ Troubleshooting
    
    - **API Key Issues**: Ensure all keys are set in secrets.toml
    - **PDF Errors**: Ensure PDFs are valid and contain extractable text
    - **Database Errors**: Verify Supabase tables are created
    - **Email Errors**: Check Gmail app password is correct
    """)

def main():
    """Main application entry point"""
    initialize_session_state()
    
    # Navigation
    with st.sidebar:
        st.title("🏥 Navigation")
        page = st.radio(
            "Go to:",
            ["Chat", "Admin Dashboard", "Instructions"],
            index=0
        )
    
    # Route to appropriate page
    if page == "Chat":
        chat_page()
    elif page == "Admin Dashboard":
        admin_dashboard_page()
    elif page == "Instructions":
        instructions_page()

if __name__ == "__main__":
    main()


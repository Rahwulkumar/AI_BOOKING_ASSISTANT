"""
Tools for the AI Booking Assistant: RAG, Booking, and Email tools
"""
from typing import Dict, Tuple, Optional
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.config import get_groq_api_key, GROQ_MODEL
from app.rag_pipeline import RAGPipeline
from db.database import get_database
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import get_email_config, SMTP_SERVER, SMTP_PORT
from datetime import datetime

# Import Groq LLM
try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

def get_llm():
    """Get Groq LLM instance"""
    if ChatGroq is None:
        raise ImportError("langchain_groq not installed. Install with: pip install langchain-groq")
    
    api_key = get_groq_api_key()
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in secrets or environment variables")
    
    return ChatGroq(
        groq_api_key=api_key,
        model_name=GROQ_MODEL,
        temperature=0.7
    )

class RAGTool:
    """Tool for answering questions using RAG"""
    
    def __init__(self):
        self.rag_pipeline = RAGPipeline()
        self.llm = get_llm()
    
    def execute(self, query: str, conversation_history: list) -> str:
        """
        Execute RAG tool: retrieve context and generate answer
        Returns answer string
        """
        try:
            # Check if vector store exists
            if st.session_state.get("vector_store") is None:
                return "I don't have any documents loaded yet. Please upload PDF files first to enable document-based answers."
            
            # Retrieve relevant chunks
            context = self.rag_pipeline.get_context_for_query(query)
            
            if "No relevant information" in context:
                return context
            
            # Format conversation history
            history_text = self._format_history(conversation_history[-10:])  # Last 10 messages for context
            
            # Create RAG prompt
            system_prompt = """You are a helpful medical appointment booking assistant. 
Answer questions based on the provided context from clinic documents. 
If the context doesn't contain the answer, say so politely.
Be concise and helpful."""
            
            prompt = f"""Context from documents:
{context}

Recent conversation:
{history_text}

User question: {query}

Please answer the user's question based on the context provided. If the context doesn't have the answer, politely say you don't have that information in the documents."""
            
            # Get LLM response
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"I encountered an error while searching the documents: {str(e)}"
    
    def _format_history(self, history: list) -> str:
        """Format conversation history for prompt"""
        formatted = []
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)

class BookingPersistenceTool:
    """Tool for saving bookings to database"""
    
    def execute(self, booking_data: Dict) -> Tuple[bool, Optional[int], str]:
        """
        Execute booking tool: save customer and booking to database
        Returns: (success: bool, booking_id: Optional[int], message: str)
        """
        try:
            db = get_database()
            
            # Validate required fields
            required = ["name", "email", "phone", "service", "date", "time"]
            missing = [field for field in required if not booking_data.get(field)]
            if missing:
                return False, None, f"Missing required fields: {', '.join(missing)}"
            
            # Get or create customer
            customer_id = db.get_or_create_customer(
                name=booking_data["name"],
                email=booking_data["email"],
                phone=booking_data["phone"]
            )
            
            # Create booking
            booking_id = db.create_booking(
                customer_id=customer_id,
                booking_type=booking_data["service"],
                date=booking_data["date"],
                time=booking_data["time"],
                status="confirmed"
            )
            
            return True, booking_id, f"Booking saved successfully with ID: {booking_id}"
            
        except Exception as e:
            return False, None, f"Error saving booking: {str(e)}"

class EmailTool:
    """Tool for sending confirmation emails"""
    
    def execute(self, to_email: str, booking_details: Dict) -> Tuple[bool, str]:
        """
        Execute email tool: send confirmation email
        Returns: (success: bool, message: str)
        """
        try:
            email_config = get_email_config()
            sender_email = email_config["sender_email"]
            sender_password = email_config["sender_password"]
            
            if not sender_email or not sender_password:
                return False, "Email credentials not configured"
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Subject'] = f"Appointment Confirmed #{booking_details.get('booking_id', 'N/A')}"
            
            # Email body
            body = f"""
Dear {booking_details.get('name', 'Valued Patient')},

Your appointment has been confirmed!

Booking Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Booking ID: #{booking_details.get('booking_id', 'N/A')}
Service: {booking_details.get('service', 'N/A')}
Date: {booking_details.get('date', 'N/A')}
Time: {booking_details.get('time', 'N/A')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please arrive 10 minutes before your scheduled time.

If you need to cancel or reschedule, please contact us at least 24 hours in advance.

Thank you for choosing our clinic!

Best regards,
Appointment Booking System
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            return True, "Email sent successfully"
            
        except smtplib.SMTPAuthenticationError:
            return False, "Email authentication failed. Please check credentials."
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            return False, f"Error sending email: {str(e)}"


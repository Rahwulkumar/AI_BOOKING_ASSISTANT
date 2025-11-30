from typing import Dict, Tuple, Optional
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.config import get_google_api_key, GEMINI_MODEL
from app.rag_pipeline import RAGPipeline
from db.database import get_database
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import get_email_config, SMTP_SERVER, SMTP_PORT
from datetime import datetime

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

def get_llm():
    if ChatGoogleGenerativeAI is None:
        raise ImportError("langchain-google-genai not installed. Install with: pip install langchain-google-genai")
    
    api_key = get_google_api_key()
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env or Streamlit secrets")
    
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=api_key,
        temperature=0.7
    )

class RAGTool:
    def __init__(self):
        self.rag_pipeline = RAGPipeline()
        self.llm = get_llm()
    
    def execute(self, query: str, conversation_history: list) -> str:
        try:
            if st.session_state.get("vector_store") is None:
                return "I don't have any documents loaded yet. Please load sample PDFs from the sidebar or upload your own documents to enable document-based answers!"
            
            context = self.rag_pipeline.get_context_for_query(query)
            
            if "No relevant information" in context:
                return "I couldn't find specific information about that in the uploaded documents. Could you rephrase your question or ask about something else? 🤔"
            
            history_text = self._format_history(conversation_history[-10:])
            
            system_prompt = """You are a friendly and knowledgeable medical appointment booking assistant. 

CRITICAL INSTRUCTIONS:
1. You MUST answer using ONLY the information provided in the "DOCUMENT CONTEXT" section below
2. Quote specific details like names, prices, times, and specialties from the documents
3. Be conversational, warm, and helpful
4. Use a friendly tone with emojis when appropriate
5. If the documents don't contain the exact answer, say so politely
6. NEVER make up information not in the documents

Your goal: Help users by providing accurate information from clinic documents in a friendly way."""
            
            prompt = f"""USER QUESTION: {query}

DOCUMENT CONTEXT (Use this information to answer):
{context}

RECENT CONVERSATION:
{history_text}

TASK: Answer the user's question using ONLY the specific information from the DOCUMENT CONTEXT above.

REQUIREMENTS:
- Quote specific names, prices, times when mentioned in documents
- Be conversational and friendly
- Use bullet points or formatting to make information clear
- If documents mention multiple options, list them
- If the context doesn't have the exact answer, say: "I don't see that specific information in the documents I have access to."

Now provide your helpful, friendly answer:"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"I encountered an error while searching the documents: {str(e)}"
    
    def _format_history(self, history: list) -> str:
        formatted = []
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)

class BookingPersistenceTool:
    def execute(self, booking_data: Dict) -> Tuple[bool, Optional[int], str]:
        try:
            db = get_database()
            
            required = ["name", "email", "phone", "service", "date", "time"]
            missing = [field for field in required if not booking_data.get(field)]
            if missing:
                return False, None, f"Missing required fields: {', '.join(missing)}"
            
            customer_id = db.get_or_create_customer(
                name=booking_data["name"],
                email=booking_data["email"],
                phone=booking_data["phone"]
            )
            
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
    def execute(self, to_email: str, booking_details: Dict) -> Tuple[bool, str]:
        try:
            email_config = get_email_config()
            sender_email = email_config["sender_email"]
            sender_password = email_config["sender_password"]
            
            if not sender_email or not sender_password:
                return False, "Email credentials not configured"
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Subject'] = f"Appointment Confirmed #{booking_details.get('booking_id', 'N/A')}"
            
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


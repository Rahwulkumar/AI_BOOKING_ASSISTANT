# 🏥 AI Doctor Appointment Booking Assistant

A complete AI-powered booking assistant with RAG (Retrieval-Augmented Generation) capabilities, conversational booking flow, email confirmations, and admin dashboard. Built with Streamlit and deployed on Streamlit Cloud.

## ✨ Features

### ✅ Core Features

1. **RAG Chatbot System**
   - Upload PDF documents via UI
   - Extract, chunk, and embed text using sentence-transformers
   - Store embeddings in FAISS vector store
   - Answer questions using retrieved context + LLM

2. **Conversational Booking Flow**
   - Intelligent intent detection (booking vs. query)
   - Multi-turn dialogue to collect:
     - Customer name
     - Email (with validation)
     - Phone number (with validation)
     - Service/booking type
     - Preferred date (YYYY-MM-DD)
     - Preferred time (HH:MM)
   - Explicit confirmation before saving
   - Conversation memory (last 25 messages)

3. **Database Storage (Supabase)**
   - PostgreSQL cloud database
   - Customers and bookings tables with foreign keys
   - Automatic customer deduplication by email
   - Persistent data storage

4. **Email Confirmation**
   - Gmail SMTP integration
   - Automatic confirmation emails with booking details
   - Graceful error handling

5. **Admin Dashboard**
   - View all bookings
   - Search by name or email
   - Export to CSV
   - Real-time data refresh

6. **Tool-Based Architecture**
   - RAG Tool: Answer questions from documents
   - Booking Persistence Tool: Save bookings to database
   - Email Tool: Send confirmation emails
   - LangChain-based tool routing

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Groq API key
- Supabase account (free tier works)
- Gmail account with app password

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI_BOOKING_ASSISTANT
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up configuration**

   Create `.streamlit/secrets.toml`:
   ```toml
   GROQ_API_KEY = "your-groq-api-key"
   SUPABASE_URL = "your-supabase-project-url"
   SUPABASE_KEY = "your-supabase-anon-key"
   GMAIL_ADDRESS = "your-email@gmail.com"
   GMAIL_APP_PASSWORD = "your-gmail-app-password"
   ```

4. **Set up Supabase database**

   Run this SQL in Supabase SQL Editor:
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

5. **Run the application**
   ```bash
   streamlit run app/main.py
   ```

## 📋 Getting API Keys

### Groq API Key

1. Visit [Groq Console](https://console.groq.com/keys)
2. Sign up or log in
3. Create a new API key
4. Copy and add to `secrets.toml`

### Supabase Setup

1. Visit [Supabase](https://supabase.com)
2. Create a new project
3. Go to **Settings > API**
4. Copy **Project URL** and **anon/public key**
5. Add to `secrets.toml`
6. Run the SQL script above in **SQL Editor**

### Gmail App Password

1. Enable **2-factor authentication** on your Gmail account
2. Go to [Google Account > Security](https://myaccount.google.com/security)
3. Under **2-Step Verification**, click **App passwords**
4. Generate a new app password for **Mail**
5. Use this 16-character password (not your regular Gmail password)

## 📁 Project Structure

```
AI_BOOKING_ASSISTANT/
├── app/
│   ├── main.py                 # Streamlit entry point
│   ├── chat_logic.py           # Intent detection, conversation
│   ├── booking_flow.py         # Slot filling, confirmation
│   ├── rag_pipeline.py         # PDF processing, RAG
│   ├── tools.py                # RAG, Booking, Email tools
│   ├── admin_dashboard.py      # Admin UI
│   ├── config.py               # Configuration
│   └── models.py               # Data models
├── db/
│   ├── database.py             # Supabase operations
│   └── models.py               # Database models
├── docs/                       # Sample PDFs
│   ├── doctors_list.pdf
│   ├── clinic_policies.pdf
│   └── services_pricing.pdf
├── requirements.txt
├── README.md
└── .streamlit/
    └── secrets.toml          # API keys (not in git)
```

## 🎯 Usage

### Chat Interface

1. **Load Documents**
   - Click "Load Sample PDFs" in sidebar, or
   - Upload your own PDF files

2. **Ask Questions**
   - "What are your operating hours?"
   - "Do you have a cardiologist?"
   - "How much does a consultation cost?"

3. **Book Appointment**
   - Say: "I want to book an appointment"
   - Follow the prompts to provide:
     - Name
     - Email
     - Phone
     - Service type
     - Date (YYYY-MM-DD)
     - Time (HH:MM)
   - Review and confirm
   - Receive booking ID and email confirmation

### Admin Dashboard

- View all bookings in a table
- Search by customer name or email
- Export data to CSV
- Refresh to see latest bookings

## 🔧 Technology Stack

- **Frontend**: Streamlit 1.29.0
- **LLM**: Groq (Llama 3.1 70B)
- **Agent Framework**: LangChain 0.1.0
- **RAG**: 
  - pdfplumber (PDF extraction)
  - sentence-transformers (embeddings)
  - FAISS (vector store)
- **Database**: Supabase (PostgreSQL)
- **Email**: Gmail SMTP

## 🚢 Deployment to Streamlit Cloud

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select repository and branch
   - Set main file path: `app/main.py`
   - Add secrets in dashboard:
     - `GROQ_API_KEY`
     - `SUPABASE_URL`
     - `SUPABASE_KEY`
     - `GMAIL_ADDRESS`
     - `GMAIL_APP_PASSWORD`
   - Click "Deploy"

3. **Verify Deployment**
   - Test PDF upload
   - Test RAG queries
   - Test booking flow
   - Test admin dashboard

## ⚠️ Troubleshooting

### API Key Issues
- Ensure all keys are set in Streamlit Cloud secrets
- Check keys are valid and have sufficient credits

### PDF Processing Errors
- Ensure PDFs contain extractable text (not scanned images)
- Check PDFs are not corrupted

### Database Errors
- Verify Supabase tables are created
- Check Supabase URL and key are correct
- Ensure foreign key constraints are set up

### Email Errors
- Verify Gmail app password (not regular password)
- Check 2FA is enabled on Gmail
- Ensure SMTP settings are correct

## 📝 Notes

- Conversation history is stored in session state (resets on refresh)
- Vector store is in-memory (resets on app restart)
- Database persists across sessions (Supabase)
- Sample PDFs are included for testing

## 📄 License

This project is created for educational/demonstration purposes.

## 👤 Author

AI Booking Assistant - Complete Implementation

---

**Ready to deploy?** Follow the deployment steps above and share your public Streamlit Cloud URL!


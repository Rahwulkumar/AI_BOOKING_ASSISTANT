# AI Doctor Appointment Booking Assistant

An intelligent, AI-powered booking assistant that uses RAG (Retrieval-Augmented Generation) to answer questions about clinic services and helps users book appointments through a conversational interface.

## Features

### Core Features
- **RAG-Powered Chatbot**: Upload PDF documents (doctor lists, services, policies) and get intelligent answers
- **Conversational Booking Flow**: Natural multi-turn dialogue to collect booking details
- **Intent Detection**: Automatically detects if user wants to book or ask questions
- **Email Confirmations**: Sends confirmation emails after successful bookings
- **Database Storage**: Persistent storage using Supabase PostgreSQL
- **Admin Dashboard**: View, search, edit, and cancel bookings
- **Find My Booking**: Users can retrieve their bookings by email, phone, or booking ID

### Interactive UI
- **Calendar Widget**: Visual date picker for appointment dates
- **Time Slot Selector**: See available vs. booked time slots
- **Service Dropdown**: Dynamic service list extracted from uploaded PDFs
- **Custom Avatars**: Visual distinction between user and bot messages

## Quick Start

### Prerequisites
- Python 3.11 or higher
- Google Gemini API Key (Get one at https://aistudio.google.com/app/apikey)
- Supabase Account (Sign up at https://supabase.com)
- Gmail Account with App Password (Setup at https://myaccount.google.com/apppasswords)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Rahwulkumar/AI_BOOKING_ASSISTANT.git
   cd AI_BOOKING_ASSISTANT
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - Copy `env_template.txt` to `.env`
   - Fill in your API keys and credentials:
     ```
     GOOGLE_API_KEY=your-google-api-key
     SUPABASE_URL=https://your-project.supabase.co
     SUPABASE_KEY=your-supabase-anon-key
     GMAIL_ADDRESS=your-email@gmail.com
     GMAIL_APP_PASSWORD=your-16-char-app-password
     ```

4. **Set up Supabase database**
   - Go to your Supabase project dashboard
   - Open SQL Editor
   - Run the SQL from `supabase_setup.sql` to create tables
   - Run the SQL from `supabase_rls_policies.sql` to enable Row Level Security

5. **Run the application**
   ```bash
   streamlit run app/main.py
   ```

## Project Structure

```
AI_BOOKING_ASSISTANT/
├── app/
│   ├── __init__.py
│   ├── main.py              # Streamlit entry point
│   ├── chat_logic.py        # Intent detection & conversation management
│   ├── booking_flow.py      # Multi-turn booking dialogue
│   ├── rag_pipeline.py      # PDF processing & vector store
│   ├── tools.py             # RAG, Booking, Email tools
│   ├── admin_dashboard.py   # Admin interface
│   ├── user_bookings.py     # User booking retrieval
│   └── config.py            # Configuration management
├── db/
│   ├── __init__.py
│   ├── database.py          # Supabase operations
│   └── models.py            # Data models
├── docs/
│   ├── doctors_list.pdf      # Sample PDF
│   ├── clinic_policies.pdf   # Sample PDF
│   └── services_pricing.pdf  # Sample PDF
├── requirements.txt          # Python dependencies
├── supabase_setup.sql       # Database schema
└── supabase_rls_policies.sql # RLS policies
```

## Configuration

### API Keys Setup

1. **Google Gemini API**
   - Visit https://aistudio.google.com/app/apikey
   - Create a new API key
   - Add to `.env` as `GOOGLE_API_KEY`

2. **Supabase**
   - Create a project at https://supabase.com
   - Get URL and anon key from Project Settings → API
   - Add to `.env` as `SUPABASE_URL` and `SUPABASE_KEY`

3. **Gmail App Password**
   - Enable 2-Step Verification on your Google Account
   - Go to https://myaccount.google.com/apppasswords
   - Generate password for "Mail" → "Other (Custom name)"
   - Use 16-character password in `.env` as `GMAIL_APP_PASSWORD`

## Deployment on Streamlit Cloud

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://streamlit.io/cloud
   - Click "New app"
   - Connect your GitHub repository
   - Set main file path: `app/main.py`
   - Add secrets in "Advanced settings":
     ```
     GOOGLE_API_KEY=your-key
     SUPABASE_URL=your-url
     SUPABASE_KEY=your-key
     GMAIL_ADDRESS=your-email
     GMAIL_APP_PASSWORD=your-password
     ```

3. **Wait for deployment** (usually 2-3 minutes)

## Usage Guide

### For Users

1. **Ask Questions**: Upload PDFs in the sidebar, then ask about services, doctors, or policies
2. **Book Appointment**: Click "Book Appointment" or type "I want to book an appointment"
3. **Fill Details**: Use interactive widgets (calendar, dropdowns, buttons) to provide information
4. **Confirm**: Review summary and confirm your booking
5. **Find Booking**: Use "Find My Booking" page to retrieve your bookings

### For Admins

1. **View Bookings**: Go to "Admin Dashboard" to see all bookings
2. **Search**: Use search bar to filter by name, email, or date
3. **Edit**: Click on a booking to edit service, date, time, or status
4. **Cancel**: Cancel bookings directly from the dashboard
5. **Export**: Download bookings as CSV

## Technologies Used

- **Frontend**: Streamlit
- **LLM**: Google Gemini 2.0 Flash
- **RAG**: FAISS Vector Store + Sentence Transformers
- **Database**: Supabase (PostgreSQL)
- **Email**: Gmail SMTP
- **PDF Processing**: pdfplumber
- **AI Framework**: LangChain

## Features Breakdown

### RAG Pipeline
- Extracts text from uploaded PDFs
- Chunks text into manageable pieces
- Creates embeddings using Sentence Transformers
- Stores in FAISS vector database
- Retrieves relevant context for LLM responses

### Booking Flow
1. Intent detection (BOOKING vs QUERY)
2. Multi-turn dialogue to collect:
   - Customer name
   - Email address
   - Phone number
   - Service type
   - Preferred date
   - Preferred time
3. Validation of all inputs
4. Summary and confirmation
5. Database persistence
6. Email confirmation

### Admin Features
- View all bookings with customer details
- Search and filter functionality
- Edit booking details
- Cancel bookings
- Export to CSV
- Statistics dashboard

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure `app/__init__.py` and `db/__init__.py` exist
   - Check Python version (3.11+)

2. **Database Connection Failed**
   - Verify Supabase credentials in `.env`
   - Ensure tables are created (run `supabase_setup.sql`)
   - Check RLS policies (run `supabase_rls_policies.sql`)

3. **Email Not Sending**
   - Verify Gmail App Password (not regular password)
   - Check 2-Step Verification is enabled
   - Ensure `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD` are correct

4. **PDF Processing Errors**
   - Ensure PDFs are not corrupted
   - Check file size (large files may timeout)

## License

This project is created for educational purposes.

## Author

Rahul Kumar


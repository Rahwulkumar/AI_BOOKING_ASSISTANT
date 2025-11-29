"""
Admin Dashboard: View and manage bookings
"""
import streamlit as st
from db.database import get_database
import pandas as pd

def admin_dashboard_page():
    """Admin dashboard page"""
    st.title("📊 Admin Dashboard - All Bookings")
    st.markdown("---")
    
    try:
        db = get_database()
        
        # Search functionality
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("🔍 Search by name or email", placeholder="Enter name or email to search...")
        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        # Fetch bookings
        if search_term:
            bookings = db.search_bookings(search_term)
            if not bookings:
                st.info(f"No bookings found matching '{search_term}'")
                return
        else:
            bookings = db.get_all_bookings()
        
        if not bookings:
            st.info("No bookings found. Bookings will appear here once customers make appointments.")
            return
        
        # Display statistics
        st.metric("Total Bookings", len(bookings))
        
        # Convert to DataFrame for better display
        df_data = []
        for booking in bookings:
            df_data.append({
                "Booking ID": booking.get("id", "N/A"),
                "Customer Name": booking.get("customer_name", "N/A"),
                "Email": booking.get("email", "N/A"),
                "Phone": booking.get("phone", "N/A"),
                "Service Type": booking.get("booking_type", "N/A"),
                "Date": booking.get("date", "N/A"),
                "Time": booking.get("time", "N/A"),
                "Status": booking.get("status", "N/A"),
                "Created At": booking.get("created_at", "N/A")
            })
        
        df = pd.DataFrame(df_data)
        
        # Display table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Export option (bonus feature)
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"bookings_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"❌ Error loading bookings: {str(e)}")
        st.info("Please ensure Supabase is configured correctly and tables are created.")


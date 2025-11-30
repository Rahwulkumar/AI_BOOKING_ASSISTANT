import streamlit as st
from db.database import get_database
from datetime import datetime

def user_bookings_page():
    st.title("🔍 Find My Booking")
    st.markdown("### Retrieve your appointment details")
    st.markdown("---")
    
    try:
        db = get_database()
        
        st.subheader("📋 Search Options")
        search_method = st.radio(
            "Search by:",
            ["Email Address", "Booking ID", "Phone Number"],
            horizontal=True
        )
        
        st.markdown("---")
        
        if search_method == "Email Address":
            search_input = st.text_input(
                "Enter your email address:",
                placeholder="your.email@example.com",
                key="email_search"
            )
            search_button_label = "🔍 Search by Email"
            
        elif search_method == "Booking ID":
            search_input = st.text_input(
                "Enter your booking ID:",
                placeholder="e.g., 1, 2, 3...",
                key="id_search"
            )
            search_button_label = "🔍 Search by Booking ID"
            
        else:
            search_input = st.text_input(
                "Enter your phone number:",
                placeholder="e.g., 1234567890",
                key="phone_search"
            )
            search_button_label = "🔍 Search by Phone"
        
        if st.button(search_button_label, use_container_width=True, type="primary"):
            if not search_input or not search_input.strip():
                st.warning("⚠️ Please enter a search term")
            else:
                with st.spinner("Searching for your bookings..."):
                    try:
                        bookings = []
                        
                        if search_method == "Email Address":
                            bookings = db.get_bookings_by_email(search_input.strip())
                        elif search_method == "Booking ID":
                            try:
                                booking_id = int(search_input.strip())
                                booking = db.get_booking_by_id(booking_id)
                                if booking:
                                    bookings = [booking]
                            except ValueError:
                                st.error("❌ Please enter a valid booking ID (numbers only)")
                                bookings = []
                        else:
                            bookings = db.get_bookings_by_phone(search_input.strip())
                        
                        if bookings:
                            st.success(f"✅ Found {len(bookings)} booking(s)!")
                            st.markdown("---")
                            
                            for idx, booking in enumerate(bookings, 1):
                                with st.container():
                                    st.markdown(f"### Booking #{idx}")
                                    
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.markdown(f"""
                                        **📋 Booking ID:** #{booking.get('id', 'N/A')}
                                        
                                        **👤 Name:** {booking.get('customer_name', 'N/A')}
                                        
                                        **📧 Email:** {booking.get('email', 'N/A')}
                                        
                                        **📱 Phone:** {booking.get('phone', 'N/A')}
                                        """)
                                    
                                    with col2:
                                        status = booking.get('status', 'N/A').title()
                                        status_color = "🟢" if status == "Confirmed" else "🔴" if status == "Cancelled" else "🟡"
                                        
                                        st.markdown(f"""
                                        **🏥 Service:** {booking.get('booking_type', 'N/A')}
                                        
                                        **📅 Date:** {booking.get('date', 'N/A')}
                                        
                                        **⏰ Time:** {booking.get('time', 'N/A')}
                                        
                                        **{status_color} Status:** {status}
                                        """)
                                    
                                    created_at = booking.get('created_at', 'N/A')
                                    if created_at != 'N/A' and isinstance(created_at, str):
                                        try:
                                            if "T" in created_at:
                                                created_at = created_at.split("T")[0]
                                        except:
                                            pass
                                    
                                    st.caption(f"📝 Created: {created_at}")
                                    
                                    if idx < len(bookings):
                                        st.markdown("---")
                        else:
                            st.info(f"ℹ️ No bookings found for the provided {search_method.lower()}.")
                            st.markdown("""
                            **Tips:**
                            - Make sure you're using the same email/phone you used when booking
                            - Check for typos in your search term
                            - If you have your booking ID, use the "Booking ID" search option
                            """)
                    
                    except Exception as e:
                        st.error(f"❌ Error searching bookings: {str(e)}")
        
        st.markdown("---")
        
        # Help section
        with st.expander("ℹ️ Need Help?"):
            st.markdown("""
            **How to find your booking:**
            
            1. **By Email:** Enter the email address you used when making the booking
            2. **By Booking ID:** Enter the booking ID you received in your confirmation email
            3. **By Phone:** Enter the phone number you used when making the booking
            
            **Note:** All bookings associated with your email/phone will be displayed.
            """)
    
    except ValueError as ve:
        st.error("❌ **Configuration Error**")
        st.markdown(f"""
        ### 🔧 Database Configuration Missing
        
        **Issue:** {str(ve)}
        
        **Solution:**
        1. Create a `.env` file in the project root
        2. Add these lines:
        ```
        SUPABASE_URL=https://your-project.supabase.co
        SUPABASE_KEY=your-supabase-anon-key
        ```
        3. Restart the application
        """)
    except Exception as e:
        error_msg = str(e)
        if "Could not find the table" in error_msg or "PGRST205" in error_msg:
            st.error("❌ **Database Tables Not Found**")
            st.markdown("""
            ### 📋 Setup Required
            
            Your Supabase database is connected, but tables haven't been created yet.
            
            Please run the SQL from `supabase_setup.sql` in your Supabase SQL Editor.
            """)
        else:
            st.error(f"❌ **Error:** {error_msg}")


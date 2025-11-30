import streamlit as st
from db.database import get_database
import pandas as pd

def admin_dashboard_page():
    st.title("📊 Admin Dashboard")
    st.markdown("### All Bookings Management")
    st.markdown("---")
    
    try:
        db = get_database()
        
        st.subheader("🔍 Search & Filter")
        
        search_col1, search_col2 = st.columns([4, 1])
        with search_col1:
            search_term = st.text_input(
                "🔍 Search by name or email",
                placeholder="Enter name or email to search...",
                key="search_input"
            )
        with search_col2:
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            if st.button("🔄 Refresh", use_container_width=True, type="primary", key="refresh_btn"):
                st.rerun()
        
        st.markdown("---")
        
        if search_term:
            bookings = db.search_bookings(search_term)
            if not bookings:
                st.info(f"ℹ️ No bookings found matching '{search_term}'")
                return
        else:
            bookings = db.get_all_bookings()
        
        if not bookings:
            st.info("ℹ️ No bookings found. Bookings will appear here once customers make appointments.")
            return
        
        st.subheader("📈 Statistics")
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.metric("Total Bookings", len(bookings))
        with stat_col2:
            confirmed_count = sum(1 for b in bookings if b.get("status") == "confirmed")
            st.metric("Confirmed", confirmed_count)
        with stat_col3:
            pending_count = sum(1 for b in bookings if b.get("status") == "pending")
            st.metric("Pending", pending_count)
        
        st.markdown("---")
        
        st.subheader("📋 All Bookings")
        
        if "editing_booking_id" not in st.session_state:
            st.session_state.editing_booking_id = None
        
        df_data = []
        for booking in bookings:
            created_at = booking.get("created_at", "N/A")
            if created_at != "N/A" and isinstance(created_at, str):
                try:
                    if "T" in created_at:
                        created_at = created_at.split("T")[0]
                except:
                    pass
            
            df_data.append({
                "ID": booking.get("id", "N/A"),
                "Customer Name": booking.get("customer_name", "N/A"),
                "Email": booking.get("email", "N/A"),
                "Phone": booking.get("phone", "N/A"),
                "Service": booking.get("booking_type", "N/A"),
                "Date": booking.get("date", "N/A"),
                "Time": booking.get("time", "N/A"),
                "Status": booking.get("status", "N/A").title(),
                "Created": created_at
            })
        
        df = pd.DataFrame(df_data)
        
        # Display table with better styling
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        st.markdown("---")
        
        # Edit and Cancel section
        st.subheader("✏️ Manage Bookings")
        
        # Booking selection for editing
        booking_ids = [b.get("id") for b in bookings if b.get("id")]
        if booking_ids:
            selected_booking_id = st.selectbox(
                "Select a booking to edit or cancel:",
                options=booking_ids,
                format_func=lambda x: f"Booking #{x}",
                key="selected_booking_for_edit"
            )
            
            if selected_booking_id:
                selected_booking = next((b for b in bookings if b.get("id") == selected_booking_id), None)
                
                if selected_booking:
                    st.markdown("### Current Booking Details")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        **Booking ID:** #{selected_booking.get('id', 'N/A')}
                        
                        **Customer Name:** {selected_booking.get('customer_name', 'N/A')}
                        
                        **Email:** {selected_booking.get('email', 'N/A')}
                        
                        **Phone:** {selected_booking.get('phone', 'N/A')}
                        """)
                    
                    with col2:
                        status = selected_booking.get('status', 'N/A').title()
                        status_emoji = "🟢" if status == "Confirmed" else "🔴" if status == "Cancelled" else "🟡"
                        st.markdown(f"""
                        **{status_emoji} Status:** {status}
                        
                        **Service:** {selected_booking.get('booking_type', 'N/A')}
                        
                        **Date:** {selected_booking.get('date', 'N/A')}
                        
                        **Time:** {selected_booking.get('time', 'N/A')}
                        """)
                    
                    st.markdown("---")
                    
                    with st.expander("✏️ Edit Booking", expanded=False):
                        edit_col1, edit_col2 = st.columns(2)
                        
                        with edit_col1:
                            new_service = st.text_input(
                                "Service Type:",
                                value=selected_booking.get('booking_type', ''),
                                key=f"edit_service_{selected_booking_id}"
                            )
                            
                            try:
                                booking_date = selected_booking.get('date', '')
                                if booking_date and booking_date != 'N/A':
                                    date_value = pd.to_datetime(booking_date).date()
                                else:
                                    from datetime import date
                                    date_value = date.today()
                            except:
                                from datetime import date
                                date_value = date.today()
                            
                            new_date = st.date_input(
                                "Date:",
                                value=date_value,
                                key=f"edit_date_{selected_booking_id}"
                            )
                        
                        with edit_col2:
                            # Parse time safely
                            try:
                                booking_time = selected_booking.get('time', '')
                                if booking_time and booking_time != 'N/A':
                                    if len(booking_time.split(':')) == 2:
                                        time_value = pd.to_datetime(booking_time, format='%H:%M').time()
                                    else:
                                        time_value = pd.to_datetime(booking_time, format='%H:%M:%S').time()
                                else:
                                    from datetime import time
                                    time_value = time(10, 0)
                            except:
                                from datetime import time
                                time_value = time(10, 0)
                            
                            new_time = st.time_input(
                                "Time:",
                                value=time_value,
                                key=f"edit_time_{selected_booking_id}"
                            )
                            new_status = st.selectbox(
                                "Status:",
                                options=["confirmed", "pending", "cancelled"],
                                index=0 if selected_booking.get('status') == "confirmed" else 1 if selected_booking.get('status') == "pending" else 2,
                                key=f"edit_status_{selected_booking_id}"
                            )
                        
                        if st.button("💾 Save Changes", key=f"save_edit_{selected_booking_id}", type="primary"):
                            try:
                                update_data = {
                                    "booking_type": new_service,
                                    "date": new_date.strftime("%Y-%m-%d") if new_date else selected_booking.get('date'),
                                    "time": new_time.strftime("%H:%M") if new_time else selected_booking.get('time'),
                                    "status": new_status
                                }
                                
                                success = db.update_booking(selected_booking_id, update_data)
                                
                                if success:
                                    st.success(f"✅ Booking #{selected_booking_id} updated successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to update booking. Please try again.")
                            except Exception as e:
                                st.error(f"❌ Error updating booking: {str(e)}")
                    
                    # Cancel booking
                    if selected_booking.get('status') != 'cancelled':
                        st.markdown("---")
                        if st.button("🚫 Cancel Booking", key=f"cancel_{selected_booking_id}", type="secondary"):
                            try:
                                success = db.cancel_booking(selected_booking_id)
                                
                                if success:
                                    st.success(f"✅ Booking #{selected_booking_id} has been cancelled!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to cancel booking. Please try again.")
                            except Exception as e:
                                st.error(f"❌ Error cancelling booking: {str(e)}")
                    else:
                        st.info("ℹ️ This booking is already cancelled.")
        
        st.markdown("---")
        
        # Export section
        st.subheader("💾 Export Data")
        csv = df.to_csv(index=False)
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"bookings_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary"
            )
        
    except ValueError as ve:
        # Supabase credentials missing
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
        
        For Streamlit Cloud: Add these as secrets in the dashboard settings.
        """)
    except Exception as e:
        error_msg = str(e)
        if "Could not find the table" in error_msg or "PGRST205" in error_msg:
            st.error("❌ **Database Tables Not Found**")
            st.markdown("""
            ### 📋 Setup Required - Create Database Tables
            
            Your Supabase database is connected, but tables haven't been created yet.
            
            **Quick Fix (2 minutes):**
            1. Go to: [Supabase Dashboard](https://supabase.com/dashboard)
            2. Select your project
            3. Click **SQL Editor** (left sidebar)
            4. Click **New Query**
            5. Copy the SQL from `supabase_setup.sql` in your project
            6. Click **Run** (or press Ctrl+Enter)
            7. Refresh this page
            
            ✅ After running the SQL, you'll see all bookings here!
            """)
        else:
            st.error(f"❌ **Unexpected Error**")
            st.markdown(f"""
            ### 🐛 Something Went Wrong
            
            **Error Details:** {error_msg}
            
            **Troubleshooting:**
            - Check your internet connection
            - Verify Supabase credentials in `.env`
            - Ensure database tables are created
            - Try refreshing the page
            
            If the issue persists, check the console for more details.
            """)


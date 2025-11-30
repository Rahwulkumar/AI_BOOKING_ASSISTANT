"""
Supabase database operations for customers and bookings
"""
from supabase import create_client, Client
from typing import List, Dict, Optional
from datetime import datetime
import streamlit as st
from app.config import get_supabase_config

class Database:
    def __init__(self):
        config = get_supabase_config()
        if not config["url"] or not config["key"]:
            raise ValueError("Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_KEY in secrets.")
        
        self.client: Client = create_client(config["url"], config["key"])
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        try:
            self.client.table("customers").select("customer_id").limit(1).execute()
        except Exception:
            pass
    
    def get_or_create_customer(self, name: str, email: str, phone: str) -> int:
        """
        Get existing customer by email or create new one
        Returns customer_id
        """
        try:
            # Check if customer exists
            result = self.client.table("customers").select("customer_id").eq("email", email).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]["customer_id"]
            else:
                new_customer = {
                    "name": name,
                    "email": email,
                    "phone": phone
                }
                result = self.client.table("customers").insert(new_customer).execute()
                if result.data:
                    return result.data[0]["customer_id"]
                else:
                    raise Exception("Failed to create customer")
        except Exception as e:
            raise Exception(f"Database error while saving customer: {str(e)}")
    
    def create_booking(self, customer_id: int, booking_type: str, date: str, time: str, status: str = "confirmed") -> int:
        try:
            new_booking = {
                "customer_id": customer_id,
                "booking_type": booking_type,
                "date": date,
                "time": time,
                "status": status
            }
            result = self.client.table("bookings").insert(new_booking).execute()
            if result.data:
                return result.data[0]["id"]
            else:
                raise Exception("Failed to create booking")
        except Exception as e:
            raise Exception(f"Database error while saving booking: {str(e)}")
    
    def get_all_bookings(self) -> List[Dict]:
        try:
            bookings_result = self.client.table("bookings").select("*").execute()
            
            if bookings_result.data:
                bookings_result.data.sort(
                    key=lambda x: x.get("created_at", ""), 
                    reverse=True
                )
            
            customers_result = self.client.table("customers").select("*").execute()
            customers_dict = {c["customer_id"]: c for c in customers_result.data}
            
            combined_bookings = []
            for booking in bookings_result.data:
                customer = customers_dict.get(booking["customer_id"], {})
                combined_booking = {
                    "id": booking["id"],
                    "customer_name": customer.get("name", "N/A"),
                    "email": customer.get("email", "N/A"),
                    "phone": customer.get("phone", "N/A"),
                    "booking_type": booking["booking_type"],
                    "date": booking["date"],
                    "time": booking["time"],
                    "status": booking["status"],
                    "created_at": booking["created_at"]
                }
                combined_bookings.append(combined_booking)
            
            return combined_bookings
        except Exception as e:
            raise Exception(f"Database error while fetching bookings: {str(e)}")
    
    def search_bookings(self, search_term: str) -> List[Dict]:
        try:
            all_bookings = self.get_all_bookings()
            search_lower = search_term.lower()
            
            filtered = [
                b for b in all_bookings
                if search_lower in b["customer_name"].lower() or search_lower in b["email"].lower()
            ]
            
            return filtered
        except Exception as e:
            raise Exception(f"Database error while searching bookings: {str(e)}")
    
    def get_booking_by_id(self, booking_id: int) -> Optional[Dict]:
        """
        Get a single booking by booking ID
        Returns booking dictionary with customer details or None
        """
        try:
            all_bookings = self.get_all_bookings()
            for booking in all_bookings:
                if booking.get("id") == booking_id:
                    return booking
            return None
        except Exception as e:
            raise Exception(f"Database error while fetching booking: {str(e)}")
    
    def get_bookings_by_email(self, email: str) -> List[Dict]:
        """
        Get all bookings for a specific email address
        Returns list of booking dictionaries
        """
        try:
            all_bookings = self.get_all_bookings()
            email_lower = email.lower()
            filtered = [
                b for b in all_bookings
                if b.get("email", "").lower() == email_lower
            ]
            return filtered
        except Exception as e:
            raise Exception(f"Database error while fetching bookings by email: {str(e)}")
    
    def get_bookings_by_phone(self, phone: str) -> List[Dict]:
        """
        Get all bookings for a specific phone number
        Returns list of booking dictionaries
        """
        try:
            all_bookings = self.get_all_bookings()
            # Normalize phone numbers for comparison (remove spaces, dashes, etc.)
            phone_normalized = ''.join(filter(str.isdigit, phone))
            filtered = []
            for booking in all_bookings:
                booking_phone = ''.join(filter(str.isdigit, booking.get("phone", "")))
                if booking_phone == phone_normalized:
                    filtered.append(booking)
            return filtered
        except Exception as e:
            raise Exception(f"Database error while fetching bookings by phone: {str(e)}")
    
    def update_booking(self, booking_id: int, booking_data: Dict) -> bool:
        """
        Update a booking with new data
        booking_data can contain: booking_type, date, time, status
        Returns True if successful, False otherwise
        """
        try:
            # Prepare update data (only include allowed fields)
            update_data = {}
            allowed_fields = ["booking_type", "date", "time", "status"]
            
            for field in allowed_fields:
                if field in booking_data:
                    update_data[field] = booking_data[field]
            
            if not update_data:
                return False
            
            # Update booking
            result = self.client.table("bookings").update(update_data).eq("id", booking_id).execute()
            
            return result.data is not None and len(result.data) > 0
        except Exception as e:
            raise Exception(f"Database error while updating booking: {str(e)}")
    
    def cancel_booking(self, booking_id: int) -> bool:
        """
        Cancel a booking by setting status to 'cancelled'
        Returns True if successful, False otherwise
        """
        try:
            result = self.client.table("bookings").update({"status": "cancelled"}).eq("id", booking_id).execute()
            return result.data is not None and len(result.data) > 0
        except Exception as e:
            raise Exception(f"Database error while cancelling booking: {str(e)}")

# Global database instance
_db_instance: Optional[Database] = None

def get_database() -> Database:
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


"""
Supabase database operations for customers and bookings
"""
from supabase import create_client, Client
from typing import List, Dict, Optional
from datetime import datetime
import streamlit as st
from app.config import get_supabase_config

class Database:
    """Database client for Supabase operations"""
    
    def __init__(self):
        """Initialize Supabase client"""
        config = get_supabase_config()
        if not config["url"] or not config["key"]:
            raise ValueError("Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_KEY in secrets.")
        
        self.client: Client = create_client(config["url"], config["key"])
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Ensure database tables exist (create if needed)"""
        # Note: In Supabase, tables should be created via SQL in the dashboard
        # This method can be used to verify connection
        try:
            # Test connection by trying to fetch (will fail if tables don't exist)
            self.client.table("customers").select("customer_id").limit(1).execute()
        except Exception as e:
            st.warning(f"⚠️ Database connection issue. Please ensure tables are created in Supabase. Error: {str(e)}")
    
    def get_or_create_customer(self, name: str, email: str, phone: str) -> int:
        """
        Get existing customer by email or create new one
        Returns customer_id
        """
        try:
            # Check if customer exists
            result = self.client.table("customers").select("customer_id").eq("email", email).execute()
            
            if result.data and len(result.data) > 0:
                # Customer exists, return existing ID
                return result.data[0]["customer_id"]
            else:
                # Create new customer
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
        """
        Create a new booking
        Returns booking ID
        """
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
        """
        Get all bookings with customer information (JOIN)
        Returns list of booking dictionaries with customer details
        """
        try:
            # Supabase doesn't support direct JOIN in Python client, so we'll fetch separately
            bookings_result = self.client.table("bookings").select("*").order("created_at", desc=True).execute()
            customers_result = self.client.table("customers").select("*").execute()
            
            # Create customer lookup
            customers_dict = {c["customer_id"]: c for c in customers_result.data}
            
            # Combine bookings with customer info
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
        """
        Search bookings by customer name or email
        Returns filtered list of bookings
        """
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

# Global database instance
_db_instance: Optional[Database] = None

def get_database() -> Database:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


"""
Data models for database operations
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Customer:
    """Customer data model"""
    customer_id: Optional[int] = None
    name: str = ""
    email: str = ""
    phone: str = ""
    created_at: Optional[datetime] = None

@dataclass
class Booking:
    """Booking data model"""
    id: Optional[int] = None
    customer_id: int = 0
    booking_type: str = ""
    date: str = ""
    time: str = ""
    status: str = "confirmed"
    created_at: Optional[datetime] = None


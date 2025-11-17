"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional

# Example schemas (retain for reference)
class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Booking schema for ECU remapping appointments
class Booking(BaseModel):
    """
    ECU Remap Booking schema
    Collection name: "booking"
    """
    name: str = Field(..., min_length=2, description="Customer full name")
    email: EmailStr = Field(..., description="Customer email")
    phone: str = Field(..., min_length=6, max_length=20, description="Contact phone number")
    vehicle: str = Field(..., description="Vehicle make & model")
    registration: str = Field(..., description="Vehicle registration/plate")
    date: str = Field(..., description="Booking date in YYYY-MM-DD format")
    time: str = Field(..., description="Booking time label, e.g., 09:00")
    notes: Optional[str] = Field(None, description="Optional notes")

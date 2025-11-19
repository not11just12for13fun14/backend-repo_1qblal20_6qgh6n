"""
Database Schemas for the Marketing CRM

Each Pydantic model represents a collection in MongoDB. The collection name is the
lowercased class name. Example: class Client -> collection "client".

These schemas are used for validation on incoming/outgoing payloads.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl, EmailStr

class Client(BaseModel):
    """
    Clients of the marketing agency
    Collection: "client"
    """
    name: str = Field(..., description="Company or client name")
    contact_name: Optional[str] = Field(None, description="Primary contact person")
    email: Optional[EmailStr] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone number")
    industry: Optional[str] = Field(None, description="Industry or vertical")
    notes: Optional[str] = Field(None, description="General notes about the client")

class Website(BaseModel):
    """
    Websites we manage for a client
    Collection: "website"
    """
    client_id: str = Field(..., description="Reference to client _id as string")
    url: HttpUrl = Field(..., description="Website URL")
    cms: Optional[str] = Field(None, description="CMS used (WordPress, Webflow, etc.)")
    status: Optional[str] = Field(None, description="Status of the site (live, staging, redesign)")
    notes: Optional[str] = Field(None, description="Notes about the site")

class SeoMetric(BaseModel):
    """
    SEO metrics snapshots per client
    Collection: "seometric"
    """
    client_id: str = Field(..., description="Reference to client _id as string")
    date: Optional[str] = Field(None, description="ISO date string for when metrics captured")
    organic_traffic: Optional[int] = Field(None, ge=0, description="Monthly organic sessions")
    keywords_top3: Optional[int] = Field(None, ge=0, description="Keywords in top 3")
    keywords_top10: Optional[int] = Field(None, ge=0, description="Keywords in top 10")
    domain_rating: Optional[float] = Field(None, ge=0, le=100, description="Authority/DR/DA score")
    notes: Optional[str] = Field(None, description="Notes on the snapshot")

class GmbProfile(BaseModel):
    """
    Google Business Profile (GMB) tracking per client
    Collection: "gmbprofile"
    """
    client_id: str = Field(..., description="Reference to client _id as string")
    listing_name: Optional[str] = Field(None, description="GBP listing name")
    url: Optional[HttpUrl] = Field(None, description="Maps/GBP URL")
    avg_rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating")
    reviews_count: Optional[int] = Field(None, ge=0, description="Number of reviews")
    primary_category: Optional[str] = Field(None, description="Primary business category")
    notes: Optional[str] = Field(None, description="Notes on profile or tasks")

# Example models kept for reference (not used by the app but can coexist)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True

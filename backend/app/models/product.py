from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    brand = Column(String, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    price = Column(Float)
    currency = Column(String, default="INR")
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    availability = Column(Boolean, default=True)
    seasonality = Column(String, nullable=True)  # e.g., "Winter", "Summer", "Festival", "Travel"
    image_url = Column(String, nullable=True)
    
    # Category-specific structured attributes (e.g. RAM, GPU, battery, size, material, wattage)
    attributes = Column(JSON, default=dict)
    
    # Keyword tags for fast indexing and hard/soft matching
    tags = Column(JSON, default=list)

    category = relationship("Category", back_populates="products")
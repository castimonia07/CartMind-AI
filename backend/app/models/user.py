from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database.connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String, default="Demo User")
    email = Column(String, unique=True, index=True, default="demo@cartmind.ai")
    preferences = Column(JSON, default=dict)  # preferred_brands, dietary, budget_limits
    
    shopping_lists = relationship("ShoppingList", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    purchase_history = relationship("PurchaseHistory", back_populates="user")
    wishlist_items = relationship("WishlistItem", back_populates="user")

class ShoppingList(Base):
    __tablename__ = "shopping_lists"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"))
    name = Column(String, default="My Basket")
    created_at = Column(DateTime, default=func.now())
    status = Column(String, default="active")  # active, completed, saved
    
    user = relationship("User", back_populates="shopping_lists")
    items = relationship("ShoppingListItem", back_populates="shopping_list", cascade="all, delete-orphan")

class ShoppingListItem(Base):
    __tablename__ = "shopping_list_items"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    shopping_list_id = Column(String(36), ForeignKey("shopping_lists.id"))
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    raw_query = Column(String)  # "2kg oats" or "Sony headphones"
    quantity = Column(Float, default=1.0)
    unit = Column(String, default="piece")
    is_checked = Column(Boolean, default=False)
    
    shopping_list = relationship("ShoppingList", back_populates="items")
    product = relationship("Product")

class PurchaseHistory(Base):
    __tablename__ = "purchase_history"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Float, default=1.0)
    price_paid = Column(Float)
    purchased_at = Column(DateTime, default=func.now())
    category_name = Column(String)
    
    user = relationship("User", back_populates="purchase_history")
    product = relationship("Product")

class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    added_at = Column(DateTime, default=func.now())
    
    user = relationship("User", back_populates="wishlist_items")
    product = relationship("Product")

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"))
    started_at = Column(DateTime, default=func.now())
    context = Column(JSON, default=dict)  # active category, hard_constraints, soft_preferences
    
    user = relationship("User", back_populates="conversations")
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id"))
    sender = Column(String)  # "USER" or "AI"
    text = Column(String)
    structured_payload = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=func.now())
    
    conversation = relationship("Conversation", back_populates="messages")
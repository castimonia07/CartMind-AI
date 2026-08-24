from pydantic import BaseModel, UUID4
from typing import Optional, List, Dict, Any

class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    brand: Optional[str] = None
    category_id: Optional[int] = None
    price: float
    currency: str = "INR"
    rating: float = 0.0
    review_count: int = 0
    availability: bool = True
    seasonality: Optional[str] = None
    image_url: Optional[str] = None
    attributes: Dict[str, Any] = {}
    tags: List[str] = []

class ProductResponse(ProductBase):
    id: int
    class Config:
        from_attributes = True

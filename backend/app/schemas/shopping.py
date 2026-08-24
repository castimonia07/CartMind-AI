from pydantic import BaseModel, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime
from .product import ProductResponse

class ShoppingListItemBase(BaseModel):
    product_id: Optional[int] = None
    raw_query: Optional[str] = None
    quantity: float = 1.0
    unit: str = "piece"

class ShoppingListItemCreate(ShoppingListItemBase):
    pass

class ShoppingListItemResponse(ShoppingListItemBase):
    id: UUID4
    shopping_list_id: UUID4
    product: Optional[ProductResponse] = None
    class Config:
        from_attributes = True

class ShoppingListBase(BaseModel):
    name: str = "My Basket"

class ShoppingListCreate(ShoppingListBase):
    pass

class ShoppingListResponse(ShoppingListBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    status: str
    items: List[ShoppingListItemResponse] = []
    class Config:
        from_attributes = True

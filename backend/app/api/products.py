from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.connection import get_db
from app.models.product import Product, Category
from app.schemas.product import ProductResponse

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("/search", response_model=List[ProductResponse])
def search_products(
    q: Optional[str] = None, 
    category: Optional[str] = None, 
    max_price: Optional[float] = None,
    brand: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    
    if category:
        cat = db.query(Category).filter(Category.name.ilike(category)).first()
        if cat:
            query = query.filter(Product.category_id == cat.id)
            
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
        
    if brand:
        query = query.filter(Product.brand.ilike(brand))
        
    return query.limit(50).all()

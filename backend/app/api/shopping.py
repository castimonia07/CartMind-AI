from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import User, ShoppingList, ShoppingListItem
from app.models.product import Product
from app.schemas.shopping import ShoppingListResponse, ShoppingListItemCreate, ShoppingListItemResponse
import uuid

# Prefix sirf /shopping rahega (main.py /api add karega)
router = APIRouter(prefix="/shopping", tags=["shopping"])

def get_current_user(db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email="demo@cartmind.ai").first()
    if not user:
        user = User(email="demo@cartmind.ai", name="Demo User")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.get("/list", response_model=ShoppingListResponse)
def get_shopping_list(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s_list = db.query(ShoppingList).filter_by(user_id=user.id, status="active").first()
    if not s_list:
        s_list = ShoppingList(user_id=user.id, name="My Basket")
        db.add(s_list)
        db.commit()
        db.refresh(s_list)
    return s_list

@router.post("/items", response_model=ShoppingListItemResponse)
def add_item(item: ShoppingListItemCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s_list = db.query(ShoppingList).filter_by(user_id=user.id, status="active").first()
    if not s_list:
        s_list = ShoppingList(user_id=user.id, name="My Basket")
        db.add(s_list)
        db.commit()
        db.refresh(s_list)
        
    db_item = ShoppingListItem(
        shopping_list_id=s_list.id,
        product_id=item.product_id,
        raw_query=item.raw_query,
        quantity=item.quantity,
        unit=item.unit
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.patch("/items/{item_id}", response_model=ShoppingListItemResponse)
def update_item(item_id: str, quantity: float, db: Session = Depends(get_db)):
    db_item = db.query(ShoppingListItem).filter(ShoppingListItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.quantity = quantity
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/items/{item_id}")
def remove_item(item_id: str, db: Session = Depends(get_db)):
    db_item = db.query(ShoppingListItem).filter(ShoppingListItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item removed"}
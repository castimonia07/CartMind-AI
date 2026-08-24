from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import User, Conversation, ConversationMessage
from app.engines.router import router_engine

# Prefix sirf /conversation rahega kyunki main.py /api add karta hai
router = APIRouter(prefix="/conversation", tags=["conversation"])

class MessageRequest(BaseModel):
    text: str
    session_id: str = "demo"

@router.post("/message")
async def send_message(req: MessageRequest, db: Session = Depends(get_db)):
    # Demo User fallback agar DB me pehla user available ho ya create karein
    user = db.query(User).first()
    if not user:
        user = User(email="demo@cartmind.ai", name="Demo User")
        db.add(user)
        db.commit()
        db.refresh(user)

    # Conversation tracking
    conv = db.query(Conversation).filter_by(user_id=user.id).first()
    if not conv:
        conv = Conversation(user_id=user.id)
        db.add(conv)
        db.commit()
        db.refresh(conv)
    
    msg_user = ConversationMessage(conversation_id=conv.id, sender="USER", text=req.text)
    db.add(msg_user)
    db.commit()

    # Route command
    result = await router_engine.route_command(req.text, user, db)

    msg_ai = ConversationMessage(conversation_id=conv.id, sender="AI", text=result.get("message", ""))
    db.add(msg_ai)
    db.commit()

    return result
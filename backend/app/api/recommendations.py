from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
from app.database.connection import get_db
from app.engines.recommendation_engine import recommendation_engine

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

class RecommendationRequest(BaseModel):
    category: str
    hard_constraints: Dict[str, Any] = {}
    soft_preferences: Dict[str, float] = {}
    
@router.post("")
def get_recommendations(req: RecommendationRequest, db: Session = Depends(get_db)):
    results = recommendation_engine.generate_recommendations(
        category_name=req.category,
        hard_constraints=req.hard_constraints,
        soft_preferences=req.soft_preferences,
        db=db
    )
    return results

from sqlalchemy.orm import Session
from app.models.product import Product
from typing import List, Dict

class SubstitutionEngine:
    def find_substitutes(self, product_id: int, db: Session, limit: int = 3) -> List[Dict]:
        target = db.query(Product).filter(Product.id == product_id).first()
        if not target:
            return []
            
        candidates = db.query(Product).filter(
            Product.category_id == target.category_id,
            Product.id != target.id
        ).all()
        
        results = []
        target_tags = set(target.tags or [])
        
        for cand in candidates:
            cand_tags = set(cand.tags or [])
            shared_tags = len(target_tags.intersection(cand_tags))
            
            # Attribute similarity
            sim = 0.5
            if shared_tags > 0:
                sim += 0.3
            if abs(cand.price - target.price) / max(target.price, 1.0) < 0.3:
                sim += 0.2
                
            results.append({
                "product": cand,
                "similarity": min(round(sim * 100, 1), 99.0),
                "price_diff": round(cand.price - target.price, 2)
            })
            
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:limit]

substitution_engine = SubstitutionEngine()
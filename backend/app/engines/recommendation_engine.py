from sqlalchemy.orm import Session
from app.models.product import Product, Category
from typing import List, Dict, Any
import copy

class RecommendationEngine:
    def generate_recommendations(
        self, 
        category_name: str, 
        hard_constraints: Dict[str, Any], 
        soft_preferences: Dict[str, float], 
        db: Session
    ) -> List[Dict]:
        # Category lookup (support fuzzy match or fallback)
        query = db.query(Product).join(Category)
        if category_name and category_name.lower() != "all":
            query = query.filter(Category.name.ilike(f"%{category_name}%"))
            
        products = query.all()
        if not products:
            # Fallback to search all products if category mismatch
            products = db.query(Product).all()
        
        # 1. Apply Strict Hard Constraints
        valid_products = [
            p for p in products 
            if self._satisfies_hard_constraints(p, hard_constraints)
        ]
        
        if not valid_products:
            # Relax budget by 15% if no strict match found
            relaxed_constraints = copy.deepcopy(hard_constraints)
            if "max_budget" in relaxed_constraints:
                relaxed_constraints["max_budget"] = relaxed_constraints["max_budget"] * 1.15
            valid_products = [
                p for p in products 
                if self._satisfies_hard_constraints(p, relaxed_constraints)
            ]

        # 2. Score Filtered Candidates
        scored_products = []
        for p in valid_products:
            score_data = self._calculate_multicriteria_score(p, soft_preferences, hard_constraints)
            scored_products.append({
                "product": {
                    "id": p.id,
                    "name": p.name,
                    "brand": p.brand,
                    "price": p.price,
                    "rating": p.rating,
                    "review_count": p.review_count,
                    "image_url": p.image_url,
                    "attributes": p.attributes or {},
                    "tags": p.tags or []
                },
                "score_breakdown": score_data,
                "total_score": score_data["total"]
            })
            
        scored_products.sort(key=lambda x: x["total_score"], reverse=True)
        return self._build_pareto_categories(scored_products)
        
    def _satisfies_hard_constraints(self, product: Product, constraints: Dict[str, Any]) -> bool:
        attrs = product.attributes or {}
        
        # Budget constraint
        if "max_budget" in constraints and constraints["max_budget"] is not None:
            if product.price > float(constraints["max_budget"]):
                return False
        if "min_budget" in constraints and constraints["min_budget"] is not None:
            if product.price < float(constraints["min_budget"]):
                return False
                
        # Electronics constraints
        if "min_ram_gb" in constraints:
            if attrs.get("ram_gb", 0) < constraints["min_ram_gb"]:
                return False
        if "max_weight_kg" in constraints:
            if attrs.get("weight_kg", 999) > constraints["max_weight_kg"]:
                return False
        if "requires_gpu" in constraints and constraints["requires_gpu"]:
            if "gpu" not in attrs or not attrs.get("ml_capable", False):
                return False
                
        # Dietary & Grocery constraints
        if "dietary_restrictions" in constraints:
            dietary_tags = [d.lower() for d in attrs.get("dietary", [])]
            for req in constraints["dietary_restrictions"]:
                if req.lower() not in dietary_tags:
                    return False
        if "dairy_free" in constraints and constraints["dairy_free"]:
            if not attrs.get("dairy_free", False):
                return False
                
        return True
        
    def _calculate_multicriteria_score(
        self, 
        product: Product, 
        preferences: Dict[str, float],
        constraints: Dict[str, Any]
    ) -> Dict[str, float]:
        attrs = product.attributes or {}
        
        # Requirement Match (base compliance)
        req_match = 0.85
        if product.rating >= 4.5:
            req_match += 0.10
        elif product.rating >= 4.0:
            req_match += 0.05
            
        # Preference Multiplier
        pref_match = 0.50
        pref_signals = []
        
        # Performance / Speed weighting
        perf_weight = preferences.get("performance", preferences.get("speed", 0.5))
        ram_val = attrs.get("ram_gb", 8)
        perf_score = min(ram_val / 16.0, 1.0)
        if attrs.get("ml_capable"):
            perf_score = 1.0
        pref_signals.append(perf_score * perf_weight)
        
        # Portability / Battery weighting
        port_weight = preferences.get("portability", preferences.get("battery", 0.5))
        weight_kg = attrs.get("weight_kg", 2.0)
        port_score = max(0.1, 1.0 - (weight_kg / 3.0))
        if attrs.get("battery_hours", 0) >= 10:
            port_score = min(1.0, port_score + 0.2)
        pref_signals.append(port_score * port_weight)
        
        # Brand Affinity
        preferred_brands = preferences.get("preferred_brands", [])
        if product.brand in preferred_brands:
            pref_signals.append(1.0)
            
        if pref_signals:
            pref_match = sum(pref_signals) / len(pref_signals)
            
        # Value Score (Quality vs Price Ratio)
        max_budget = constraints.get("max_budget", product.price * 1.5)
        price_efficiency = max(0.1, 1.0 - (product.price / max(max_budget, 1.0)))
        value_score = (price_efficiency * 0.6) + ((product.rating / 5.0) * 0.4)
        
        # Combined Weighted Aggregate
        total = (req_match * 0.40) + (pref_match * 0.35) + (value_score * 0.25)
        
        return {
            "total": round(total * 100, 1),
            "requirement_match": round(min(req_match, 1.0) * 100, 1),
            "preference_match": round(min(pref_match, 1.0) * 100, 1),
            "value": round(min(value_score, 1.0) * 100, 1)
        }
        
    def _build_pareto_categories(self, scored_products: List[Dict]) -> List[Dict]:
        if not scored_products:
            return []
            
        res = []
        # 1. Best Match (Overall champion)
        best_match = copy.deepcopy(scored_products[0])
        best_match["tag"] = "BEST MATCH"
        best_match["explanation"] = f"Top aggregate score ({best_match['total_score']}%) meeting both specs and personal weights."
        res.append(best_match)
        
        # 2. Best Value (Max value score among remainder)
        if len(scored_products) > 1:
            remainder = scored_products[1:]
            value_sort = sorted(remainder, key=lambda x: x["score_breakdown"]["value"], reverse=True)
            best_val = copy.deepcopy(value_sort[0])
            best_val["tag"] = "BEST VALUE"
            best_val["explanation"] = f"Optimal price-to-performance tradeoff with ₹{int(best_val['product']['price']):,} price point."
            res.append(best_val)
            
        # 3. Premium / Top Spec Pick
        if len(scored_products) > 2:
            remainder_premium = [p for p in scored_products if p["product"]["id"] not in [r["product"]["id"] for r in res]]
            if remainder_premium:
                premium_sort = sorted(remainder_premium, key=lambda x: x["product"]["price"], reverse=True)
                top_spec = copy.deepcopy(premium_sort[0])
                top_spec["tag"] = "TOP SPEC"
                top_spec["explanation"] = "Highest performance specs without budget compromise."
                res.append(top_spec)
                
        return res

recommendation_engine = RecommendationEngine()
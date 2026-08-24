from app.agents.intent_parser import intent_parser, IntentResult
from app.engines.recommendation_engine import recommendation_engine
from app.engines.substitution_engine import substitution_engine
from sqlalchemy.orm import Session
from app.models.user import User, ShoppingList, ShoppingListItem, PurchaseHistory
from app.models.product import Product

class CommandRouter:
    async def route_command(self, text: str, user: User, db: Session):
        intent_res: IntentResult = await intent_parser.parse_intent(text)

        fast_intents = ["ADD_ITEM", "REMOVE_ITEM", "UPDATE_QUANTITY", "CLEAR_CART", "SHOW_CART"]
        if intent_res.intent in fast_intents:
            return await self._handle_fast_path(intent_res, user, db)
        else:
            return await self._handle_decision_path(intent_res, user, db)

    def _get_or_create_list(self, user: User, db: Session) -> ShoppingList:
        s_list = db.query(ShoppingList).filter_by(user_id=user.id, status="active").first()
        if not s_list:
            s_list = ShoppingList(user_id=user.id, name="My Basket")
            db.add(s_list)
            db.commit()
            db.refresh(s_list)
        return s_list

    async def _handle_fast_path(self, intent_res: IntentResult, user: User, db: Session):
        s_list = self._get_or_create_list(user, db)

        if intent_res.intent == "ADD_ITEM":
            added = []
            for item in intent_res.items:
                raw = item.get("raw_query", "").strip()
                qty = float(item.get("quantity", 1.0))
                unit = item.get("unit", "piece")
                if not raw:
                    continue
                
                # Check fuzzy DB match
                product = db.query(Product).filter(
                    Product.name.ilike(f"%{raw}%")
                ).first()
                
                new_item = ShoppingListItem(
                    shopping_list_id=s_list.id,
                    product_id=product.id if product else None,
                    raw_query=raw,
                    quantity=qty,
                    unit=unit
                )
                db.add(new_item)
                added.append(f"{qty} {unit} {raw}" if unit != "piece" else f"{raw} (x{int(qty)})")
                
            db.commit()
            return {
                "status": "success",
                "message": f"✓ Added {', '.join(added)} to your basket.",
                "mode": "fast",
                "intent": "ADD_ITEM"
            }

        elif intent_res.intent == "REMOVE_ITEM":
            removed = []
            for item in intent_res.items:
                raw = item.get("raw_query", "").strip().lower()
                db_item = db.query(ShoppingListItem).filter(
                    ShoppingListItem.shopping_list_id == s_list.id,
                    ShoppingListItem.raw_query.ilike(f"%{raw}%")
                ).first()
                
                if not db_item:
                    all_items = db.query(ShoppingListItem).filter_by(shopping_list_id=s_list.id).all()
                    for i in all_items:
                        if i.product and raw in i.product.name.lower():
                            db_item = i
                            break
                            
                if db_item:
                    db.delete(db_item)
                    removed.append(raw)
                    
            db.commit()
            if removed:
                return {"status": "success", "message": f"✓ Removed {', '.join(removed)} from basket.", "mode": "fast", "intent": "REMOVE_ITEM"}
            return {"status": "warning", "message": "Could not find that item in your basket.", "mode": "fast", "intent": "REMOVE_ITEM"}

        elif intent_res.intent == "CLEAR_CART":
            db.query(ShoppingListItem).filter_by(shopping_list_id=s_list.id).delete()
            db.commit()
            return {"status": "success", "message": "✓ Basket cleared.", "mode": "fast", "intent": "CLEAR_CART"}

        elif intent_res.intent == "SHOW_CART":
            return {"status": "success", "message": "Here's your current basket.", "mode": "fast", "intent": "SHOW_CART"}

        return {"status": "error", "message": "Unknown command.", "mode": "fast"}

    async def _handle_decision_path(self, intent_res: IntentResult, user: User, db: Session):
        if intent_res.intent == "RECOMMEND":
            cat_name = intent_res.category or "Electronics"
            
            # Merge user profile preferences into soft_preferences
            merged_prefs = dict(user.preferences or {})
            merged_prefs.update(intent_res.soft_preferences or {})
            
            results = recommendation_engine.generate_recommendations(
                category_name=cat_name,
                hard_constraints=intent_res.hard_constraints or {},
                soft_preferences=merged_prefs,
                db=db
            )
            
            budget = intent_res.hard_constraints.get("max_budget") if intent_res.hard_constraints else None
            msg_parts = [f"Found {len(results)} tailored recommendation(s)"]
            if budget:
                msg_parts.append(f"within ₹{int(budget):,} budget")

            return {
                "status": "success",
                "message": " ".join(msg_parts) + ".",
                "mode": "decision",
                "intent": "RECOMMEND",
                "extracted_constraints": intent_res.hard_constraints,
                "extracted_preferences": intent_res.soft_preferences,
                "extracted_category": cat_name,
                "recommendations": results
            }

        elif intent_res.intent == "FIND_SUBSTITUTE":
            s_list = self._get_or_create_list(user, db)
            items = db.query(ShoppingListItem).filter_by(shopping_list_id=s_list.id).all()
            if items:
                last_matched = next((i for i in reversed(items) if i.product_id), None)
                if last_matched and last_matched.product:
                    subs = substitution_engine.find_substitutes(last_matched.product.id, db)
                    return {
                        "status": "success",
                        "message": f"Found {len(subs)} alternative(s) for {last_matched.product.name}.",
                        "mode": "decision",
                        "intent": "FIND_SUBSTITUTE",
                        "substitutes": [
                            {
                                "id": s["product"].id,
                                "name": s["product"].name,
                                "price": s["product"].price,
                                "similarity": s["similarity"],
                                "price_diff": s["price_diff"]
                            }
                            for s in subs
                        ]
                    }
            return {"status": "info", "message": "Add an item to your basket first to find substitutes.", "mode": "decision", "intent": "FIND_SUBSTITUTE"}

        return {
            "status": "info",
            "message": "Specify your needs (e.g., 'Laptop under ₹80k for ML' or 'Add 2kg oats').",
            "mode": "decision",
            "intent": intent_res.intent
        }

router_engine = CommandRouter()